from datetime import datetime, timedelta
import random
from db.database import SessionLocal
from db.models import (
    DailyStory,
    User,
    UserWord,
    Word
)
from collections import Counter
from services.gemini_service import generate_story


def get_user_words_for_story(telegram_id: int, max_words: int = 15, recent_words: int = 100):
    """
    Выбираем тему для истории дня с учётом изученных слов
    и возвращаем тему + список слов этой темы.
    Взвешенный случайный выбор темы, чтобы не зацикливаться только на самой частой теме.
    """

    db = SessionLocal()
    try:
        # Получаем пользователя
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        if not user:
            return None, []

        # Берём последние recent_words изученных слов
        user_words = (
            db.query(UserWord)
            .filter(UserWord.user_id == user.id)  # локальный user id
            .filter(UserWord.learned_at.isnot(None))
            .order_by(UserWord.learned_at.desc())
            .limit(recent_words)
            .all()
        )

        if not user_words:
            return None, []

        # Получаем все слова по id
        word_ids = [uw.word_id for uw in user_words]
        words = db.query(Word).filter(Word.id.in_(word_ids)).all()
        if not words:
            return None, []

        # Считаем количество слов по темам
        topic_counter = Counter(word.topic for word in words)
        topics, counts = zip(*topic_counter.items())
        total = sum(counts)
        weights = [count / total for count in counts]

        # Случайный выбор темы с учётом веса
        selected_topic = random.choices(topics, weights=weights, k=1)[0]

        # Берём слова выбранной темы
        topic_words = [w.lemma for w in words if w.topic == selected_topic]

        # Ограничиваем по max_words
        selected_words = topic_words[:max_words]

        print(f"[DAILY STORY] Topic: {selected_topic}")
        print(f"[DAILY STORY] Words: {selected_words}")

        return selected_topic, selected_words

    finally:
        db.close()


def get_daily_story(
    telegram_id: int
):
    """
    Возвращает историю за сегодня,
    если она уже была создана.
    """

    db = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(
                User.telegram_id == telegram_id
            )
            .first()
        )

        if not user:
            return None

        today = datetime.utcnow().date()

        story = (
            db.query(DailyStory)
            .filter(
                DailyStory.user_id == user.id
            )
            .filter(
                DailyStory.story_date == today
            )
            .first()
        )

        return story

    finally:

        db.close()


def create_daily_story(
    telegram_id: int,
    topic: str,
    words: list
):
    """
    Создает историю через Gemini
    и сохраняет в БД.
    """

    if not words:
        return None

    db = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(
                User.telegram_id == telegram_id
            )
            .first()
        )

        if not user:
            return None
     
        story_text = generate_story(
            topic,
            words
        )

        if (
            not story_text
            or story_text.startswith("Ошибка Gemini")
            or story_text.startswith("⚠️")
        ):
            return None

        today = datetime.utcnow().date()

        story = DailyStory(
            user_id=user.id,
            story_date=today,
            story_text=story_text
        )

        db.add(
            story
        )

        db.commit()

        db.refresh(
            story
        )

        return story

    finally:

        db.close()
