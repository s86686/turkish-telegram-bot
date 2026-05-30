# services/word_service.py

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


def get_random_word(
    telegram_id: int
):

    db = SessionLocal()

    try:

        user = db.query(
            User
        ).filter(
            User.telegram_id == telegram_id
        ).first()

        if not user:
            return None

        # 1. Слова к повторению

        review_word = (
            db.query(
                UserWord
            )
            .filter(
                UserWord.user_id == user.id,
                UserWord.next_review <= datetime.utcnow()
            )
            .first()
        )

        if review_word:

            word = db.query(
                Word
            ).filter(
                Word.id == review_word.word_id
            ).first()

        else:

            learned_ids = [
                uw.word_id
                for uw in db.query(
                    UserWord
                ).filter(
                    UserWord.user_id == user.id
                ).all()
            ]

            new_words = (
                db.query(
                    Word
                )
                .filter(
                    ~Word.id.in_(learned_ids)
                )
                .all()
            )

            if new_words:

                word = random.choice(
                    new_words
                )

            else:

                word = random.choice(
                    db.query(Word).all()
                )

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

        all_words = []

        for w in db.query(
            Word
        ).all():

            all_words.append(
                {
                    "id": w.id,
                    "translation": w.translation
                }
            )

        result["quiz"] = build_quiz(
            result,
            all_words
        )

        return result

    finally:

        db.close()
