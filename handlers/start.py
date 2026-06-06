from aiogram import Router
from aiogram.filters import CommandStart

from aiogram.filters import Command

from services.gemini_service import (
    explain_phrase
)

from aiogram.types import Message

from services.users import (
    get_or_create_user
)

from keyboards.menu import (
    main_menu
)

router = Router()


@router.message(CommandStart())
async def start(
    message: Message
):

    get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username
    )

    await message.answer(
        "🇹🇷 Добро пожаловать в Turkish Learning Bot\n\n"
        "Каждый день:\n"
        "• новые слова\n"
        "• повторения по Anki\n"
        "• мини-тесты\n\n"
        "Нажмите «📚 Урок» чтобы начать.",
        reply_markup=main_menu
    )

@router.message(
    Command("test_ai")
)
async def test_ai(
    message: Message
):

    result = explain_phrase(
        "Phaselis'te ineceğim."
    )

    await message.answer(
        result
    )
