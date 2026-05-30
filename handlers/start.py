from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def start(message: Message):

    await message.answer(
        "🇹🇷 Turkish Learning Bot\n\n"
        "Команды:\n"
        "/lesson - начать урок\n"
        "/stats - статистика"
    )
