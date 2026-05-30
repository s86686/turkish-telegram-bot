from db.database import SessionLocal

from db.models import (
    User,
    UserWord
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
            w.correct_count
            for w in words
        )

        wrong = sum(
            w.wrong_count
            for w in words
        )

        return {
            "learned": learned,
            "correct": correct,
            "wrong": wrong
        }

    finally:
        db.close()
