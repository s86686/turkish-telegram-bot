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

        query = (
            db.query(Word)
            .filter(
                ~Word.id.in_(learned_ids)
            )
        )

        if user.selected_topic != "all":

            query = query.filter(
                Word.topic
                == user.selected_topic
            )

        new_words = query.all()

        if not new_words:

            if user.selected_topic != "all":
                return "TOPIC_FINISHED"
        
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
                    Word.id,
                    Word.lemma,
                    Word.translation
                )
                .all()
            )
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

            db.delete(
                review
            )

            db.commit()

            return get_review_word(
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
                    Word.id,
                    Word.lemma,
                    Word.translation
                )
                .all()
            )
        ]

        return build_word_result(
            word,
            all_words,
            user.quiz_direction
        )

    finally:

        db.close()
