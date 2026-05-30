from aiogram import Router

from aiogram.types import Message

router = Router()


@router.message(
    lambda m: m.text == "📈 Статистика"
)
async def stats(
    message: Message
):

    await message.answer(
        "📈 Статистика пока недоступна."
    )
