from datetime import datetime

from db.database import SessionLocal
from db.models import (
    DailyStory,
    User,
    UserWord,
    Word
)

from services.gemini_service import generate_story


def get_user_words_for_story(
    telegram_id: int,
    limit: int = 10
):
    """
    Получаем последние изученные слова пользователя.
    telegram_id приходит из Telegram.
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
            .limit(limit)
            .all()
        )

        words = []

        for uw in user_words:

            word = (
                db.query(Word)
                .filter(
                    Word.id == uw.word_id
                )
                .first()
            )

            if word:
                words.append(
                    word.lemma
                )

        return words

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

        if (
            not story_text
            or story_text.startswith("Ошибка Gemini")
            or story_text.startswith("⚠️")
        ):
            return None

        story_text = generate_story(
            words
        )

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
