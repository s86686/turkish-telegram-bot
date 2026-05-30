from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from services.users import (
    get_or_create_user
)

router = Router()


@router.message(CommandStart())
async def start(message: Message):

    get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username
    )

    await message.answer(
        "🇹🇷 Добро пожаловать!\n\n"
        "Команда:\n"
        "/lesson"
    )
