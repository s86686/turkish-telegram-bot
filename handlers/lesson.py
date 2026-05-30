from aiogram import Router
from aiogram import F

from aiogram.types import (
    Message,
    CallbackQuery
)

from services.dictionary import (
    get_random_word
)

from keyboards.review import (
    show_answer_keyboard,
    quality_keyboard
)

from keyboards.review import (
    show_answer_keyboard,
    quality_keyboard,
    quiz_keyboard,
    continue_keyboard
)

router = Router()

CURRENT_WORDS = {}


@router.message(
    lambda m: m.text == "📚 Урок"
)
async def lesson(
    message: Message
):

    word = get_random_word()

    CURRENT_WORDS[
        message.from_user.id
    ] = word

    await message.answer(
        f"🇹🇷\n\n"
        f"{word['lemma']}",
        reply_markup=
        show_answer_keyboard()
    )


@router.callback_query(
    F.data == "show_answer"
)
async def show_answer(
    callback: CallbackQuery
):

    word = CURRENT_WORDS.get(
        callback.from_user.id
    )

    if not word:
        return

    example = word["examples"][0]

    await callback.message.edit_text(
        f"🇹🇷 {word['lemma']}\n\n"
        f"🇷🇺 {word['translation']}\n\n"
        f"{example['tr']}\n"
        f"{example['ru']}"
    )

    await callback.message.answer(
        f"Что означает:\n\n"
        f"🇹🇷 {word['lemma']} ?",
        reply_markup=quiz_keyboard(
        word["quiz"]["options"]
        )
    )

    await callback.answer()


@router.callback_query(
    F.data.startswith("q_")
)
async def rate_word(
    callback: CallbackQuery
):

    quality = callback.data.split(
        "_"
    )[1]

    await callback.message.answer(
        f"Оценка сохранена: {quality}\n\n"
        f"Нажмите 📚 Урок для следующего слова."
    )

    await callback.answer()

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

    if selected == correct:

        text = "✅ Верно"

    else:

        answer = (
            word["quiz"]["options"][
                correct
            ]
        )

        text = (
            f"❌ Неверно\n\n"
            f"Правильный ответ:\n"
            f"{answer}"
        )

    await callback.message.edit_text(
        text,
        reply_markup=quality_keyboard()
    )

    await callback.answer()
