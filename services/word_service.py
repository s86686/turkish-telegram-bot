import random

from datetime import datetime

from db.database import SessionLocal
from db.models import (
    Word,
    User,
    UserWord
)

from services.quiz_service import (
    build_quiz
)


def build_word_result(
    word,
    all_words
):

    result = {
        "id": word.id,
        "lemma": word.lemma,
        "translation": word.translation,
        "examples": [
            {
                "tr": word.example_tr,
                "ru": word.example_ru
            }
        ]
    }

    result["quiz"] = build_quiz(
        result,
        all_words
    )

    return result


def get_new_word(
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

        learned_ids = [
            uw.word_id
            for uw in db.query(
                UserWord
            ).filter(
                UserWord.user_id == user.id
            ).all()
        ]

        new_words = (
            db.query(Word)
            .filter(
                ~Word.id.in_(learned_ids)
            )
            .all()
        )

        if not new_words:
            return None

        word = random.choice(
            new_words
        )

        all_words = [
            {
                "id": w.id,
                "translation": w.translation
            }
            for w in db.query(
                Word
            ).all()
        ]

        return build_word_result(
            word,
            all_words
        )

    finally:

        db.close()


def get_review_word(
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
            db.query(UserWord)
            .filter(
                UserWord.user_id == user.id,
                UserWord.next_review <= datetime.utcnow()
            )
            .order_by(
                UserWord.next_review
            )
            .first()
        )

        if not review:
            return None

        word = (
            db.query(Word)
            .filter(
                Word.id == review.word_id
            )
            .first()
        )

        if not word:
            return None

        all_words = [
            {
                "id": w.id,
                "translation": w.translation
            }
            for w in db.query(
                Word
            ).all()
        ]

        return build_word_result(
            word,
            all_words
        )

    finally:

        db.close()
