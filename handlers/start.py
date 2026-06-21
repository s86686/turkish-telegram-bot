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

from db.database import SessionLocal
from db.models import User

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

from services.english_word_service import (
    get_new_english_word
)


@router.message(
    Command("engtest")
)
async def eng_test(
    message: Message
):

    word = get_new_english_word(
        message.from_user.id
    )

    if not word:

        await message.answer(
            "Нет английских слов для изучения."
        )

        return

    quiz = word["quiz"]

    text = (
        f"🇬🇧 {word['lemma']}\n\n"
        f"🇷🇺 {word['translation']}\n\n"
        f"Question:\n"
        f"{quiz['question']}\n\n"
        f"Options:\n"
    )

    for i, option in enumerate(
        quiz["options"],
        start=1
    ):

        text += (
            f"{i}. {option}\n"
        )

    text += (
        f"\nCorrect: "
        f"{quiz['correct'] + 1}"
    )

    await message.answer(
        text
    )

@router.message(Command("english"))
async def switch_english(
    message: Message
):

    db = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(
                User.telegram_id == message.from_user.id
            )
            .first()
        )

        if user:

            user.learning_language = "en"

            db.commit()

        await message.answer(
            "🇬🇧 English C2 activated"
        )

    finally:

        db.close()


@router.message(Command("turkish"))
async def switch_turkish(
    message: Message
):

    db = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(
                User.telegram_id == message.from_user.id
            )
            .first()
        )

        if user:

            user.learning_language = "tr"

            db.commit()

        await message.answer(
            "🇹🇷 Turkish activated"
        )

    finally:

        db.close()
