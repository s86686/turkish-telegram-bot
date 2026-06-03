from aiogram import Router
from aiogram import F

from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from keyboards.settings import (
    direction_keyboard
)

from services.settings_service import (
    get_direction,
    set_direction
)

from services.topic_service import (
    get_topics,
    get_topic_name,
    get_user_topic,
    set_user_topic
)

router = Router()


def topics_keyboard():

    topics = get_topics()

    keyboard = [
        [
            InlineKeyboardButton(
                text="🌍 Все слова",
                callback_data="topic_all"
            )
        ]
    ]

    for topic in topics:

        keyboard.append(
            [
                InlineKeyboardButton(
                    text=get_topic_name(
                        topic
                    ),
                    callback_data=f"topic_{topic}"
                )
            ]
        )

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )


@router.message(
    lambda m: m.text == "⚙ Настройки"
)
async def settings(
    message: Message
):

    direction = get_direction(
        message.from_user.id
    )

    current_topic = get_user_topic(
        message.from_user.id
    )

    topic_name = (
        "🌍 Все слова"
        if current_topic == "all"
        else get_topic_name(
            current_topic
        )
    )

    if direction == "RU_TR":

        text = (
            "⚙ Настройки\n\n"
            "Текущее направление:\n"
            "🇷🇺 → 🇹🇷\n\n"
            f"Текущая тема:\n{topic_name}"
        )

    else:

        text = (
            "⚙ Настройки\n\n"
            "Текущее направление:\n"
            "🇹🇷 → 🇷🇺\n\n"
            f"Текущая тема:\n{topic_name}"
        )

    await message.answer(
        text,
        reply_markup=direction_keyboard()
    )


@router.callback_query(
    F.data == "dir_tr_ru"
)
async def dir_tr_ru(
    callback: CallbackQuery
):

    set_direction(
        callback.from_user.id,
        "TR_RU"
    )

    await callback.message.edit_text(
        "✅ Направление изменено\n\n"
        "🇹🇷 → 🇷🇺"
    )

    await callback.answer()


@router.callback_query(
    F.data == "dir_ru_tr"
)
async def dir_ru_tr(
    callback: CallbackQuery
):

    set_direction(
        callback.from_user.id,
        "RU_TR"
    )

    await callback.message.edit_text(
        "✅ Направление изменено\n\n"
        "🇷🇺 → 🇹🇷"
    )

    await callback.answer()


@router.callback_query(
    F.data == "choose_topic"
)
async def choose_topic(
    callback: CallbackQuery
):

    current_topic = get_user_topic(
        callback.from_user.id
    )

    topic_name = (
        "🌍 Все слова"
        if current_topic == "all"
        else get_topic_name(
            current_topic
        )
    )

    await callback.message.edit_text(
        f"📚 Тема изучения\n\n"
        f"Текущая тема:\n"
        f"{topic_name}\n\n"
        f"Выберите новую тему:",
        reply_markup=topics_keyboard()
    )

    await callback.answer()


@router.callback_query(
    lambda c: c.data.startswith(
        "topic_"
    )
)
async def set_topic(
    callback: CallbackQuery
):

    topic = callback.data.replace(
        "topic_",
        ""
    )

    set_user_topic(
        callback.from_user.id,
        topic
    )

    topic_name = (
        "🌍 Все слова"
        if topic == "all"
        else get_topic_name(
            topic
        )
    )

    await callback.message.edit_text(
        f"✅ Тема изменена\n\n"
        f"{topic_name}"
    )

    await callback.answer()
