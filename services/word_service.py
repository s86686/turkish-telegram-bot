import random

from db.database import SessionLocal
from db.models import Word


def get_random_word():

    db = SessionLocal()

    try:

        words = db.query(
            Word
        ).all()

        if not words:
            return None

        return random.choice(
            words
        )

    finally:

        db.close()
