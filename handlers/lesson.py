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

from services.english_word_service import (
    get_new_english_word,
    get_review_english_word
)

from services.language_service import (
    get_learning_language
)

from services.english_review_service import (
    save_english_review
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
VOICE_MESSAGES = {}
CURRENT_MODE = {}
SPEAK_IN_PROGRESS = set()

def build_question_text(
    word
):

    question = word["quiz"]["question"]

    flag = (
        "🇬🇧"
        if word.get("language") == "en"
        else "🇹🇷"
    )

    if question == word["lemma"]:

        title = "Что означает?"
        text = f"{flag} {question}"

    else:

        if word.get("language") == "en":

            title = "Как будет по-английски?"

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

    language = get_learning_language(
        message.from_user.id
    )
    
    if language == "en":
    
        word = get_new_english_word(
            message.from_user.id
        )
    
    else:
    
        word = get_new_word(
            message.from_user.id
        )

    if word == "LIMIT_REACHED":

        await message.answer(
            "🎉 Лимит новых слов на сегодня достигнут.\n\n"
            "Перейдите к повторениям 🔁"
        )

        return

    if word == "TOPIC_FINISHED":

        await message.answer(
            "🎉 Вы изучили все новые слова этой темы.\n\n"
            "Выберите другую тему в настройках ⚙ "
            "или перейдите к повторениям 🔁"
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

    CURRENT_MODE[
        message.from_user.id
    ] = "new"
    
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

    language = get_learning_language(
        message.from_user.id
    )
    
    if language == "en":
    
        word = get_review_english_word(
            message.from_user.id
        )
    
    else:
    
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

    CURRENT_MODE[
        message.from_user.id
    ] = "review"
    
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
    
    if word.get("language") == "en":
    
        flag = "🇬🇧"
    
        example_text = (
            f"{example['en']}\n"
            f"{example['ru']}"
        )
    
    else:
    
        flag = "🇹🇷"
    
        example_text = (
            f"{example['tr']}\n"
            f"{example['ru']}"
        )
    
    await callback.message.edit_text(
        f"{result}\n\n"
        f"{flag} {word['lemma']}\n"
        f"🇷🇺 {word['translation']}\n\n"
        f"{example_text}",
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

    language = get_learning_language(
        callback.from_user.id
    )
    
    if language == "en":
    
        interval = save_english_review(
            telegram_id=callback.from_user.id,
            word_id=word["id"],
            quality=quality
        )
    
    else:
    
        interval = save_review(
            telegram_id=callback.from_user.id,
            word_id=word["id"],
            quality=quality
        )

    await callback.message.edit_text(
        f"✅ Ответ сохранён\n\n"
        f"📅 Следующее повторение через "
        f"{interval} дн.",
        reply_markup=next_word_keyboard(
            CURRENT_MODE.get(
                callback.from_user.id,
                "new"
            )
        )
    )

    await callback.answer()


@router.callback_query(
    F.data == "speak"
)
async def speak_word(
    callback: CallbackQuery
):

    await callback.answer()

    user_id = callback.from_user.id

    word = CURRENT_WORDS.get(
        callback.from_user.id
    )

    if not word:

        await callback.message.answer(
            "DEBUG: word not found"
        )

        return

    if user_id in SPEAK_IN_PROGRESS:

        await callback.message.answer(
            "DEBUG: already in progress"
        )

        return

    SPEAK_IN_PROGRESS.add(
        user_id
    )

    try:

        await callback.message.answer(
            f"DEBUG 1\nLanguage: {word.get('language')}"
        )

        example = word["examples"][0]

        if word.get("language") == "en":

            text = (
                f"{word['lemma']}. "
                f"{example['en']}"
            )

        else:

            text = (
                f"{word['lemma']}. "
                f"{example['tr']}"
            )

        await callback.message.answer(
            f"DEBUG 2\n{text}"
        )

        filename = await generate_tts(
            text,
            language=word.get(
                "language",
                "tr"
            )
        )

        await callback.message.answer(
            f"DEBUG 3\nFile: {filename}"
        )

        audio = FSInputFile(
            filename
        )

        voice_msg = await callback.message.answer_voice(
            audio
        )

        await callback.message.answer(
            "DEBUG 4\nVoice sent"
        )

        VOICE_MESSAGES[
            callback.from_user.id
        ] = voice_msg.message_id

    except Exception as e:

        await callback.message.answer(
            f"❌ TTS ERROR:\n{e}"
        )

    finally:

        try:

            if (
                'filename' in locals()
                and os.path.exists(filename)
            ):
                os.remove(filename)

        except Exception:
            pass

        SPEAK_IN_PROGRESS.discard(
            user_id
        )

    

@router.callback_query(
    F.data.startswith("next_")
)
async def next_word(
    callback: CallbackQuery
):

    voice_message_id = VOICE_MESSAGES.get(
        callback.from_user.id
    )

    if voice_message_id:

        try:

            await callback.bot.delete_message(
                chat_id=callback.message.chat.id,
                message_id=voice_message_id
            )

        except Exception:
            pass

        VOICE_MESSAGES.pop(
            callback.from_user.id,
            None
        )

    mode = callback.data.split("_")[1]

    language = get_learning_language(
        callback.from_user.id
    )
    
    if language == "en":
    
        if mode == "review":
    
            word = get_review_english_word(
                callback.from_user.id
            )
    
        else:
    
            word = get_new_english_word(
                callback.from_user.id
            )
    
    else:
    
        if mode == "review":
    
            word = get_review_word(
                callback.from_user.id
            )
    
        else:
    
            word = get_new_word(
                callback.from_user.id
            )

    if mode == "new" and word == "LIMIT_REACHED":

        await callback.message.edit_text(
            "🎉 Лимит новых слов на сегодня достигнут.\n\n"
            "Перейдите к повторениям 🔁"
        )

        await callback.answer()

        return

    if mode == "new" and word == "TOPIC_FINISHED":

        await callback.message.edit_text(
            "🎉 Вы изучили все новые слова этой темы.\n\n"
            "Выберите другую тему в настройках ⚙ "
            "или перейдите к повторениям 🔁"
        )
    
        await callback.answer()
    
        return

    if not word:

        if mode == "review":

            await callback.message.edit_text(
                "🎉 Сегодня повторений нет."
            )

        else:

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

