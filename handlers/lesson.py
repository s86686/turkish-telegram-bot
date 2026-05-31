from aiogram import Router
from aiogram import F

from aiogram.types import (
    Message,
    CallbackQuery,
    FSInputFile
)

from services.word_service import (
    get_random_word
)

from services.review_service import (
    save_review
)

from services.tts_service import (
    generate_tts
)

from keyboards.review import (
    quality_keyboard,
    quiz_keyboard,
    next_word_keyboard
)

router = Router()

CURRENT_WORDS = {}


@router.message(
    lambda m: m.text == "📚 Урок"
)
async def lesson(
    message: Message
):

    word = get_random_word(
        message.from_user.id
    )

    if not word:

        await message.answer(
            "Слова не найдены."
        )

        return

    CURRENT_WORDS[
        message.from_user.id
    ] = word

    await message.answer(
        f"Что означает?\n\n"
        f"🇹🇷 {word['lemma']}",
        reply_markup=quiz_keyboard(
            word["quiz"]["options"]
        )
    )


@router.callback_query(
    F.data.startswith("quiz_")
)
async def process_quiz(
    callback: CallbackQuery
):

    word = CURRENT_WORDS.get(
        callback.from_user.id
    )

    if not word:
        return

    selected = int(
        callback.data.split("_")[1]
    )

    correct = (
        word["quiz"]["correct"]
    )

    example = word["examples"][0]

    if selected == correct:

        result = "✅ Верно"

    else:

        result = (
            "❌ Неверно\n\n"
            f"Правильный ответ:\n"
            f"{word['translation']}"
        )

    await callback.message.edit_text(
        f"{result}\n\n"
        f"🇹🇷 {word['lemma']}\n"
        f"🇷🇺 {word['translation']}\n\n"
        f"{example['tr']}\n"
        f"{example['ru']}",
        reply_markup=quality_keyboard()
    )

    await callback.answer()


@router.callback_query(
    F.data.startswith("q_")
)
async def rate_word(
    callback: CallbackQuery
):

    quality = int(
        callback.data.split("_")[1]
    )

    word = CURRENT_WORDS.get(
        callback.from_user.id
    )

    if not word:
        return

    save_review(
        telegram_id=callback.from_user.id,
        word_id=word["id"],
        quality=quality
    )

    await callback.message.edit_text(
        "✅ Ответ сохранён",
        reply_markup=next_word_keyboard()
    )

    await callback.answer()


@router.callback_query(
    F.data == "speak"
)
async def speak_word(
    callback: CallbackQuery
):

    word = CURRENT_WORDS.get(
        callback.from_user.id
    )

    if not word:
        return

    example = word["examples"][0]

    text = (
        f"{word['lemma']}. "
        f"{example['tr']}"
    )

    filename = await generate_tts(
        text
    )

    audio = FSInputFile(
        filename
    )

    await callback.message.answer_voice(
        audio
    )

    await callback.answer()

@router.callback_query(
    F.data == "next_word"
)
async def next_word(
    callback: CallbackQuery
):

    word = get_random_word(
        callback.from_user.id
    )

    if not word:

        await callback.answer(
            "Слова не найдены."
        )

        return

    CURRENT_WORDS[
        callback.from_user.id
    ] = word

    await callback.message.edit_text(
        f"Что означает?\n\n"
        f"🇹🇷 {word['lemma']}",
        reply_markup=quiz_keyboard(
            word["quiz"]["options"]
        )
    )

    await callback.answer()
