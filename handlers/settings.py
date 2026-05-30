from aiogram import Router

from aiogram.types import Message

router = Router()


@router.message(
    lambda m: m.text == "⚙ Настройки"
)
async def settings(
    message: Message
):

    await message.answer(
        "⚙ Настройки появятся позже."
    )
