import random

from datetime import datetime

from db.database import SessionLocal

from db.models import (
    User,
    EnglishWord,
    UserEnglishWord
)

from services.quiz_service import (
    build_quiz
)


def build_word_result(
    word,
    all_words,
    direction
):

    result = {
        "id": word.id,
        "language": "en",
        "lemma": word.lemma,
        "translation": word.translation,
        "examples": [
            {
                "en": word.example_en,
                "ru": word.example_ru
            }
        ]
    }

    result["quiz"] = build_quiz(
        result,
        all_words,
        direction
    )

    return result


def get_new_english_word(
    telegram_id: int
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

        today = datetime.utcnow().date()

        learned_today = (
            db.query(UserEnglishWord)
            .filter(
                UserEnglishWord.user_id == user.id
            )
            .all()
        )

        learned_today_count = len(
            [
                w for w in learned_today
                if w.learned_at
                and w.learned_at.date() == today
            ]
        )

        if learned_today_count >= user.daily_new_words:
            return "LIMIT_REACHED"

        learned_ids = [
            uw.word_id
            for uw in (
                db.query(UserEnglishWord)
                .filter(
                    UserEnglishWord.user_id == user.id
                )
                .all()
            )
        ]

        new_words = (
            db.query(EnglishWord)
            .filter(
                ~EnglishWord.id.in_(
                    learned_ids
                )
            )
            .all()
        )

        if not new_words:
            return None

        best_priority = min(
            w.priority
            for w in new_words
        )

        candidates = [

            w

            for w in new_words

            if w.priority == best_priority

        ]

        word = random.choice(
            candidates
        )

        all_words = [
            {
                "id": row.id,
                "lemma": row.lemma,
                "translation": row.translation
            }
            for row in (
                db.query(
                    EnglishWord.id,
                    EnglishWord.lemma,
                    EnglishWord.translation
                )
                .all()
            )
        ]

        return build_word_result(
            word,
            all_words,
            "EN_RU"
        )

    finally:

        db.close()

def get_review_english_word(
    telegram_id: int
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

        review = (
            db.query(UserEnglishWord)
            .filter(
                UserEnglishWord.user_id == user.id,
                UserEnglishWord.next_review <= datetime.utcnow()
            )
            .order_by(
                UserEnglishWord.next_review
            )
            .first()
        )

        if not review:
            return None

        word = (
            db.query(EnglishWord)
            .filter(
                EnglishWord.id == review.word_id
            )
            .first()
        )

        if not word:

            db.delete(
                review
            )

            db.commit()

            return get_review_english_word(
                telegram_id
            )

        all_words = [
            {
                "id": row.id,
                "lemma": row.lemma,
                "translation": row.translation
            }
            for row in (
                db.query(
                    EnglishWord.id,
                    EnglishWord.lemma,
                    EnglishWord.translation
                )
                .all()
            )
        ]

        return build_word_result(
            word,
            all_words,
            "EN_RU"
        )

    finally:

        db.close()
