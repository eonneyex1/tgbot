import os
from dotenv import load_dotenv
import asyncio
import random
import string
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

load_dotenv()

TOKEN = os.getenv("TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Состояния для опроса пользователя
class PassGen(StatesGroup):
    waiting_for_length = State()
    waiting_for_symbols = State()

def get_main_keyboard():
    return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🎲 Сгенерировать пароль")]], resize_keyboard=True)

def get_symbols_keyboard():
    buttons = [
        [InlineKeyboardButton(text="✅ Да", callback_data="symbols_yes")],
        [InlineKeyboardButton(text="❌ Нет (только буквы и цифры)", callback_data="symbols_no")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_again_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Создать другой пароль", callback_data="start_over")]
    ])

def generate_password(length, use_symbols):
    chars = string.ascii_letters + string.digits
    if use_symbols:
        # Убираем <, > и &, чтобы HTML-разметка в Telegram не ломалась
        punctuation = string.punctuation.replace('<', '').replace('>', '').replace('&', '')
        chars += punctuation
    return ''.join(random.choice(chars) for _ in range(length))

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Нажми кнопку ниже, чтобы создать надежный пароль.", reply_markup=get_main_keyboard())

@dp.message(F.text == "🎲 Сгенерировать пароль")
async def ask_length(message: types.Message, state: FSMContext):
    await message.answer("Введите желаемую длину пароля (числом от 4 до 64):")
    await state.set_state(PassGen.waiting_for_length)

@dp.message(PassGen.waiting_for_length)
async def process_length(message: types.Message, state: FSMContext):
    if not message.text.isdigit() or int(message.text) < 4 or int(message.text) > 64:
        await message.answer("Пожалуйста, введите целое число от 4 до 64.")
        return
    
    await state.update_data(length=int(message.text))
    await message.answer("Добавлять в пароль спецсимволы (@#$%)?", reply_markup=get_symbols_keyboard())
    await state.set_state(PassGen.waiting_for_symbols)

@dp.callback_query(PassGen.waiting_for_symbols, F.data.startswith("symbols_"))
async def finish_gen(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    length = user_data.get('length', 12)
    use_symbols = callback.data == "symbols_yes"
    
    password = generate_password(length, use_symbols)
    
    await callback.message.answer(
        f"Ваш пароль ({length} симв.):\n<code>{password}</code>", 
        parse_mode="HTML",
        reply_markup=get_again_keyboard()
    )
    await state.clear()
    await callback.answer()

@dp.callback_query(F.data == "start_over")
async def process_start_over(callback: types.CallbackQuery, state: FSMContext):
    # Убираем кнопку из старого сообщения, чтобы не нажимали дважды
    await callback.message.edit_reply_markup(reply_markup=None)
    # Снова спрашиваем длину
    await ask_length(callback.message, state)
    await callback.answer()

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Выключено")
