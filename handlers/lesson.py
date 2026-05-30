from aiogram import Router
from aiogram.filters import Command

from aiogram.types import Message

from services.vocabulary import get_first_word

router = Router()


@router.message(Command("lesson"))
async def lesson(message: Message):

    word = get_first_word()

    if not word:
        await message.answer(
            "Словарь пуст."
        )
        return

    await message.answer(
        f"📖 Слово:\n\n"
        f"{word['lemma']}\n\n"
        f"Нажмите 'Показать перевод'"
    )
