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
    all_words,
    direction
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
        all_words,
        direction
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

        today = datetime.utcnow().date()

        learned_today = (
            db.query(UserWord)
            .filter(
                UserWord.user_id == user.id
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
                "id": w.id,
                "lemma": w.lemma,
                "translation": w.translation
            }
            for w in db.query(
                Word
            ).all()
        ]

        return build_word_result(
            word,
            all_words,
            user.quiz_direction
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
            return {
                "error": "USER_NOT_FOUND"
            }

        reviews_count = (
            db.query(UserWord)
            .filter(
                UserWord.user_id == user.id
            )
            .count()
        )

        ready_count = (
            db.query(UserWord)
            .filter(
                UserWord.user_id == user.id,
                UserWord.next_review <= datetime.utcnow()
            )
            .count()
        )

        return {
            "telegram_id": telegram_id,
            "user_id": user.id,
            "reviews_count": reviews_count,
            "ready_count": ready_count
        }

    finally:

        db.close()
