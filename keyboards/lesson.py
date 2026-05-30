from aiogram.types import InlineKeyboardMarkup
from aiogram.types import InlineKeyboardButton


show_translation_keyboard = (
    InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👁 Показать перевод",
                    callback_data="show_translation"
                )
            ]
        ]
    )
)
