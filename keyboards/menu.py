from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton
)


main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="📚 Урок"
            )
        ],
        [
            KeyboardButton(
                text="📈 Статистика"
            ),
            KeyboardButton(
                text="⚙ Настройки"
            )
        ]
    ],
    resize_keyboard=True
)
