from aiogram import Router
from aiogram import F

from aiogram.types import (
Message,
CallbackQuery,
FSInputFile
)

from services.word_service import (
get_new_word,
get_review_word
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

def build_question_text(
word
):


question = word["quiz"]["question"]

if question == word["lemma"]:

    title = "Что означает?"

    text = f"🇹🇷 {question}"

else:

    title = "Как будет по-турецки?"

    text = f"🇷🇺 {question}"

return f"{title}\n\n{text}"


@router.message(
lambda m: m.text == "📚 Новые слова"
)
async def new_words(
message: Message
):


word = get_new_word(
    message.from_user.id
)

if word == "LIMIT_REACHED":

    await message.answer(
        "🎉 Лимит новых слов на сегодня достигнут.\n\n"
        "Перейдите к повторениям 🔁"
    )

    return

if not word:

    await message.answer(
        "🎉 Новых слов больше нет."
    )

    return

CURRENT_WORDS[
    message.from_user.id
] = word

await message.answer(
    build_question_text(word),
    reply_markup=quiz_keyboard(
        word["quiz"]["options"]
    )
)


@router.message(
lambda m: m.text == "🔁 Повторения"
)
async def reviews(
message: Message
):


word = get_review_word(
    message.from_user.id
)

if not word:

    await message.answer(
        "🎉 Сегодня повторений нет."
    )

    return

CURRENT_WORDS[
    message.from_user.id
] = word

await message.answer(
    build_question_text(word),
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

interval = save_review(
    telegram_id=callback.from_user.id,
    word_id=word["id"],
    quality=quality
)

await callback.message.edit_text(
    f"✅ Ответ сохранён\n\n"
    f"📅 Следующее повторение через "
    f"{interval} дн.",
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


word = get_new_word(
    callback.from_user.id
)

if word == "LIMIT_REACHED":

    await callback.message.edit_text(
        "🎉 Лимит новых слов на сегодня достигнут.\n\n"
        "Перейдите к повторениям 🔁"
    )

    await callback.answer()

    return

if not word:

    await callback.message.edit_text(
        "🎉 Новых слов больше нет."
    )

    await callback.answer()

    return

CURRENT_WORDS[
    callback.from_user.id
] = word

await callback.message.edit_text(
    build_question_text(word),
    reply_markup=quiz_keyboard(
        word["quiz"]["options"]
    )
)

await callback.answer()
