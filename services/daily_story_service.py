from datetime import datetime, timedelta

from db.database import SessionLocal
from db.models import (
    DailyStory,
    User,
    UserWord,
    Word
)
from collections import Counter
from services.gemini_service import generate_story


def get_user_words_for_story(
    telegram_id: int,
    max_words: int = 15
):
    """
    Выбираем доминирующую тему среди изученных слов
    и возвращаем слова этой темы для истории.
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
            return []

        user_words = (
            db.query(UserWord)
            .filter(
                UserWord.user_id == user.id
            )
            .filter(
                UserWord.learned_at.isnot(None)
            )
            .order_by(
                UserWord.learned_at.desc()
            )
            .limit(100)
            .all()
        )

        if not user_words:
            return []

        word_ids = [
            uw.word_id
            for uw in user_words
        ]

        words = (
            db.query(Word)
            .filter(
                Word.id.in_(word_ids)
            )
            .all()
        )

        if not words:
            return []

        topic_counter = Counter(
            word.topic
            for word in words
        )

        best_topic = (
            topic_counter
            .most_common(1)[0][0]
        )

        topic_words = [
            word.lemma
            for word in words
            if word.topic == best_topic
        ]

        print(
            f"[DAILY STORY] Topic: {best_topic}"
        )

        print(
            f"[DAILY STORY] Words: {topic_words}"
        )

        return topic_words[:max_words]

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
