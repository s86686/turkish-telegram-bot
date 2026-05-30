from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

def continue_keyboard():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="➡ Продолжить",
                    callback_data="start_quiz"
                )
            ]
        ]
    )

def show_answer_keyboard():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👁 Показать перевод",
                    callback_data="show_answer"
                )
            ]
        ]
    )


def quality_keyboard():

    return InlineKeyboardMarkup(
        inline_keyboard=[
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
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
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

from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)


def speak_keyboard():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔊 Слушать",
                    callback_data="speak"
                )
            ]
        ]
    )
