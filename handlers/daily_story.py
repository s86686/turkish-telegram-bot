from aiogram import Router, F
from aiogram.types import Message
from services.daily_story_service import get_daily_story, get_user_words_for_story, create_daily_story

router = Router()

@router.message(lambda m: m.text == "📖 История дня")
async def show_daily_story(message: Message):
    user_id = message.from_user.id

    story = get_daily_story(user_id)
    if story:
        await message.answer(f"📖 История дня:\n\n{story.story_text}")
        return

    words = get_user_words_for_story(user_id)
    if not words:
        await message.answer("Сегодня ещё нет изученных слов для истории.")
        return

    story = create_daily_story(user_id, words)
    await message.answer(f"📖 История дня:\n\n{story.story_text}")
