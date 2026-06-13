from aiogram import Router, F
from aiogram.types import Message
from services.daily_story_service import get_daily_story, get_user_words_for_story, create_daily_story, filter_unknown_words
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)
from aiogram.enums import ParseMode
from services.gemini_service import (
    extract_new_words
)
router = Router()

daily_story_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="❌ Закрыть",
                callback_data="close_story"
            )
        ]
    ]
)

@router.message(lambda m: m.text == "📖 История дня")
async def show_daily_story(message: Message):

    user_id = message.from_user.id

# Сначала пробуем получить готовую историю
story = get_daily_story(user_id)

if story:

    await message.answer(
        story.story_text,
        reply_markup=daily_story_keyboard,
        parse_mode=ParseMode.HTML
    )

    return

# Если истории нет — создаем по изученным словам
topic, words = get_user_words_for_story(
    user_id
)

if not words:

    await message.answer(
        "Сегодня ещё нет изученных слов для истории."
    )

    return

story = create_daily_story(
    user_id,
    topic,
    words
)

if not story or not story.story_text:

    await message.answer(
        "⚠️ Не удалось сгенерировать историю. Попробуйте позже."
    )

    return

new_words = extract_new_words(
    story.story_text
)

new_words = filter_unknown_words(
    new_words
)

if new_words:

    debug_text = "\n\n🆕 Найдено новых слов:\n\n"

    for word in new_words:

        debug_text += (
            f"• {word['lemma']} — "
            f"{word['translation']} "
            f"({word['topic']})\n"
        )

    story.story_text += debug_text

await message.answer(
    story.story_text,
    reply_markup=daily_story_keyboard,
    parse_mode=ParseMode.HTML
)


    
@router.callback_query(lambda c: c.data == "close_story")
async def close_story(callback: CallbackQuery):
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.answer()
