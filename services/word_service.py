# services/word_service.py

import random

from db.database import SessionLocal
from db.models import Word

from services.quiz_service import (
    build_quiz
)


def get_random_word():

    db = SessionLocal()

    try:

        words = db.query(
            Word
        ).all()

        if not words:
            return None

        word = random.choice(
            words
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

        for w in words:

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
