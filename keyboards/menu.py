from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton
)


main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📚 Новые слова"),
            KeyboardButton(text="🔁 Повторения")
        ],
        [
            KeyboardButton(
                text="📈 Статистика"
            ),
            KeyboardButton(
                text="⚙ Настройки"
            )
        ],
        [
            KeyboardButton(
                text="🎭 Диалоги"
            )
        ]
    ],
    resize_keyboard=True
)
