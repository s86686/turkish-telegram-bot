from aiogram import Router

from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)

from dialogs.cafe import (
    CAFE_DIALOGS
)

router = Router()

topics_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="☕ Кафе",
                callback_data="dialog_cafe"
            )
        ],
        [
            InlineKeyboardButton(
                text="🏨 Отель",
                callback_data="dialog_hotel"
            )
        ],
        [
            InlineKeyboardButton(
                text="🚕 Такси",
                callback_data="dialog_taxi"
            )
        ],
        [
            InlineKeyboardButton(
                text="✈️ Аэропорт",
                callback_data="dialog_airport"
            )
        ]
    ]
)

dialog_back_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="⬅️ Назад к темам",
                callback_data="dialogs_menu"
            )
        ]
    ]
)


@router.message(
    lambda m: m.text == "🎭 Диалоги"
)
async def dialogs_menu(
    message: Message
):

    await message.answer(
        "🎭 Выберите тему:",
        reply_markup=topics_keyboard
    )


@router.callback_query(
    lambda c: c.data == "dialogs_menu"
)
async def back_to_dialogs_menu(
    callback: CallbackQuery
):

    await callback.message.edit_text(
        "🎭 Выберите тему:",
        reply_markup=topics_keyboard
    )

    await callback.answer()


@router.callback_query(
    lambda c: c.data == "dialog_cafe"
)
async def show_cafe_dialog(
    callback: CallbackQuery
):

    dialog = CAFE_DIALOGS[0]

    text = (
        f"🎭 {dialog['title']}\n\n"
    )

    for line in dialog["lines"]:

        speaker = (
            "👨‍🍳 Garson"
            if line["speaker"] == "Garson"
            else "👤 Siz"
        )

        text += (
            f"{speaker}\n"
            f"🇹🇷 {line['tr']}\n"
            f"🇷🇺 {line['ru']}\n\n"
        )

    await callback.message.edit_text(
        text,
        reply_markup=dialog_back_keyboard
    )

    await callback.answer()
