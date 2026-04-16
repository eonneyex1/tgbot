import os
from dotenv import load_dotenv
import asyncio
import random
import string
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

load_dotenv()

TOKEN = os.getenv("TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()


def get_main_keyboard():
    btn_generate = KeyboardButton(text="🎲 Сгенерировать пароль")
    return ReplyKeyboardMarkup(keyboard=[[btn_generate]], resize_keyboard=True)


def get_length_keyboard():
    buttons = [
        [InlineKeyboardButton(text="8", callback_data="len_8")],
        [InlineKeyboardButton(text="12", callback_data="len_12")],
        [InlineKeyboardButton(text="16", callback_data="len_16")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)



def generate_password(length):
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(chars) for _ in range(length))

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Нажми кнопку ниже.", reply_markup=get_main_keyboard())


@dp.message(F.text == "🎲 Сгенерировать пароль")
async def ask_length(message: types.Message):
    await message.answer("Выберите длину будущего пароля:", reply_markup=get_length_keyboard())


@dp.callback_query(F.data.startswith("len_"))
async def process_password_gen(callback: types.CallbackQuery):
    
    length = int(callback.data.split("_")[1])
    
    password = generate_password(length)
    
    
    await callback.message.answer(f"Ваш пароль на {length} символов:\n`{password}`", parse_mode="MarkdownV2")
    await callback.answer()

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Выключено")