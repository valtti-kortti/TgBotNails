from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

def keyboard(text, n):
    keyboard = InlineKeyboardBuilder()
    for key, val in text.items():
        keyboard.add(InlineKeyboardButton(text=key, callback_data=val))
    return keyboard.adjust(n).as_markup()