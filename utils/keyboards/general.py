
from ast import List
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_buttons(buttons: List, adjust: List = [1]):
    builder = InlineKeyboardBuilder()
    for button in buttons:
        builder.button(**button)
    builder.adjust(*adjust)

    return builder.as_markup()