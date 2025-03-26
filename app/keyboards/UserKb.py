from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

def keyboard(text, n):
    keyboard = InlineKeyboardBuilder()
    for key, val in text.items():
        keyboard.add(InlineKeyboardButton(text=key, callback_data=val))
    return keyboard.adjust(n).as_markup()


def main_menu():
    text = {
            "Записаться на услугу": "zap", 
            "Отменить запись": "antizap",
            "Настройки": "settigs",
            "Прайс лист": "price_list",
            "Мои записи": "myzap",
            }
    return keyboard(text, 2)

def register():
    text = {
            "Да": "reg_1",
            "Нет": "reg_0",
            }
    return keyboard(text, 2)