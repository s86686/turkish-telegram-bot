from aiogram import Router
from aiogram import F

from aiogram.types import (
    Message,
    CallbackQuery
)

from keyboards.settings import (
    direction_keyboard
)

from services.settings_service import (
    get_direction,
    set_direction
)

router = Router()


@router.message(
    lambda m: m.text == "⚙ Настройки"
)
async def settings(
    message: Message
):

    direction = get_direction(
        message.from_user.id
    )

    if direction == "RU_TR":

        text = (
            "⚙ Настройки\n\n"
            "Текущее направление:\n"
            "🇷🇺 → 🇹🇷"
        )

    else:

        text = (
            "⚙ Настройки\n\n"
            "Текущее направление:\n"
            "🇹🇷 → 🇷🇺"
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
