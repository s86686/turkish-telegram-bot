from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)


def quality_keyboard():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔊 Слушать",
                    callback_data="speak"
                )
            ],
            [
                InlineKeyboardButton(
                    text="😵 Забыл",
                    callback_data="q_0"
                ),
                InlineKeyboardButton(
                    text="😕 Трудно",
                    callback_data="q_1"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🙂 Хорошо",
                    callback_data="q_2"
                ),
                InlineKeyboardButton(
                    text="😎 Легко",
                    callback_data="q_3"
                )
            ]
        ]
    )

def quiz_keyboard(options):

    keyboard = []

    for index, option in enumerate(options):

        keyboard.append(
            [
                InlineKeyboardButton(
                    text=option,
                    callback_data=f"quiz_{index}"
                )
            ]
        )

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )

def next_word_keyboard():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➡ Следующее слово",
                    callback_data="next_word"
                )
            ]
        ]
    )
