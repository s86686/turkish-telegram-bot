from datetime import datetime

from db.database import SessionLocal

from db.models import (
    User,
    UserWord,
    Word
)


def get_stats(
    telegram_id
):

    db = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(
                User.telegram_id
                == telegram_id
            )
            .first()
        )

        if not user:
            return None

        words = (
            db.query(UserWord)
            .filter(
                UserWord.user_id
                == user.id
            )
            .all()
        )

        learned = len(words)

        correct = sum(
            (w.correct_count or 0)
            for w in words
        )

        wrong = sum(
            (w.wrong_count or 0)
            for w in words
        )

        review_today = len(
            [
                w for w in words
                if w.next_review
                and w.next_review <= datetime.utcnow()
            ]
        )

        total_words = (
            db.query(Word)
            .count()
        )

        new_words = (
            total_words
            - learned
        )

        return {
            "learned": learned,
            "correct": correct,
            "wrong": wrong,
            "review_today": review_today,
            "new_words": new_words
        }

    finally:

        db.close()
