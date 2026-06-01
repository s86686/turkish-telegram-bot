from aiogram import Router

from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    FSInputFile
)

from services.tts_service import (
    generate_tts
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


def dialog_keyboard(
    dialog_index: int
):

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔊 Озвучить диалог",
                    callback_data=f"cafe_speak_{dialog_index}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="➡️ Следующий диалог",
                    callback_data=f"cafe_next_{dialog_index}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад к темам",
                    callback_data="dialogs_menu"
                )
            ]
        ]
    )


def build_dialog_text(
    dialog
):

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

    return text


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

    await callback.message.edit_text(
        build_dialog_text(dialog),
        reply_markup=dialog_keyboard(0)
    )

    await callback.answer()


@router.callback_query(
    lambda c: c.data.startswith(
        "cafe_next_"
    )
)
async def next_cafe_dialog(
    callback: CallbackQuery
):

    current_index = int(
        callback.data.split("_")[2]
    )

    next_index = (
        current_index + 1
    ) % len(CAFE_DIALOGS)

    dialog = CAFE_DIALOGS[
        next_index
    ]

    await callback.message.edit_text(
        build_dialog_text(dialog),
        reply_markup=dialog_keyboard(
            next_index
        )
    )

    await callback.answer()

@router.callback_query(
    lambda c: c.data.startswith(
        "cafe_speak_"
    )
)
async def speak_cafe_dialog(
    callback: CallbackQuery
):

    dialog_index = int(
        callback.data.split("_")[2]
    )

    dialog = CAFE_DIALOGS[
        dialog_index
    ]

    text = " ".join(
        line["tr"]
        for line in dialog["lines"]
    )

    import os

    filename = await generate_tts(
        text
    )

    try:

        audio = FSInputFile(
            filename
        )

        await callback.message.answer_voice(
            audio
        )

    finally:

        if os.path.exists(
            filename
        ):
            os.remove(
                filename
            )

    await callback.answer()

