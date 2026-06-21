from datetime import datetime

from db.database import SessionLocal

from db.models import (
    User,
    UserWord,
    Word,
    UserEnglishWord,
    EnglishWord
)


def get_stats(
    telegram_id
):

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

        if user.learning_language == "en":

            words = (
                db.query(UserEnglishWord)
                .filter(
                    UserEnglishWord.user_id
                    == user.id
                )
                .all()
            )

            total_words = (
                db.query(EnglishWord)
                .count()
            )

        else:

            words = (
                db.query(UserWord)
                .filter(
                    UserWord.user_id
                    == user.id
                )
                .all()
            )

            total_words = (
                db.query(Word)
                .count()
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

        new_words = (
            total_words
            - learned
        )

        today = datetime.utcnow().date()

        learned_today = len(
            [
                w for w in words
                if w.learned_at
                and w.learned_at.date() == today
            ]
        )

        return {
            "learned": learned,
            "correct": correct,
            "wrong": wrong,
            "review_today": review_today,
            "new_words": new_words,
            "learned_today": learned_today,
            "daily_limit": user.daily_new_words
        }

    finally:

        db.close()
