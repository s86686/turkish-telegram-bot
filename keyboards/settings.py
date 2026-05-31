from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)


def direction_keyboard():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🇹🇷 → 🇷🇺",
                    callback_data="dir_tr_ru"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🇷🇺 → 🇹🇷",
                    callback_data="dir_ru_tr"
                )
            ]
        ]
    )
