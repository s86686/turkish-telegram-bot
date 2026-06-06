from db.database import SessionLocal
from db.models import DailyStory, UserWord, Word
from datetime import datetime
from services.gemini_service import explain_phrase
from sqlalchemy import func


def get_user_words_for_story(user_id: int, limit: int = 10):
    """Берем слова, которые пользователь изучал сегодня"""
    db = SessionLocal()
    today = datetime.utcnow().date()
    try:
        # Используем func.date для сравнения только даты без времени
        user_words = (
            db.query(UserWord)
            .filter(UserWord.user_id == user_id)
            .filter(UserWord.learned_at != None)
            .filter(func.date(UserWord.learned_at) == today)
            .order_by(UserWord.next_review)
            .limit(limit)
            .all()
        )

        words = []
        for uw in user_words:
            word = db.query(Word).filter(Word.id == uw.word_id).first()
            if word:
                words.append(word.lemma)
        return words
    finally:
        db.close()


def get_daily_story(user_id: int):
    """Возвращает историю дня для пользователя, если она есть"""
    db = SessionLocal()
    today = datetime.utcnow().date()
    try:
        story = (
            db.query(DailyStory)
            .filter(DailyStory.user_id == user_id)
            .filter(DailyStory.story_date == today)
            .first()
        )
        return story
    finally:
        db.close()


def create_daily_story(user_id: int, words: list):
    """Создаем историю через Gemini и сохраняем в БД"""
    if not words:
        return None  # защита от пустого списка слов

    db = SessionLocal()
    today = datetime.utcnow().date()
    try:
        prompt = f"""
Ты преподаватель турецкого языка.
Напиши короткую историю уровня A1-A2.
Используй все эти слова: {', '.join(words)}
5-8 предложений, простой турецкий, естественная ситуация.
После истории дай перевод на русский.
Выделяй использованные слова жирным.
"""
        story_text = explain_phrase(prompt)

        story = DailyStory(
            user_id=user_id,
            story_date=today,
            story_text=story_text
        )

        db.add(story)
        db.commit()
        db.refresh(story)
        return story
    finally:
        db.close()
