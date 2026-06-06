from db.database import SessionLocal
from db.models import DailyStory, UserWord, Word
from datetime import datetime
from services.gemini_service import generate_story  # отдельная функция для генерации истории


def get_user_words_for_story(user_id: int, limit: int = 10):
    """Берем слова, которые пользователь изучал сегодня"""
    db = SessionLocal()
    today = datetime.utcnow().date()
    try:
        user_words = (
            db.query(UserWord)
            .filter(UserWord.user_id == user_id)
            .filter(UserWord.learned_at != None)
            .filter(UserWord.learned_at >= today)
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
    db = SessionLocal()
    today = datetime.utcnow().date()
    try:
        # Генерируем историю через отдельную функцию
        story_text = generate_story(words)

        story = DailyStory(
            user_id=user_id,
            story_date=today,
            story_text=story_text
        )

        db.add(story)
        db.commit()
        return story
    finally:
        db.close()
