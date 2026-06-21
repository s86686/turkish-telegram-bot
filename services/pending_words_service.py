from db.database import SessionLocal
from db.models import (
    User,
    PendingWord
)


def save_pending_words(
    telegram_id: int,
    language: str,
    words: list
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
            return 0

        (
            db.query(PendingWord)
            .filter(
                PendingWord.user_id == user.id
            )
            .delete()
        )

        db.commit()

        saved = 0

        for word in words:

            pending_word = PendingWord(
                user_id=user.id,
                language=language,
                lemma=word["lemma"],
                translation=word["translation"],
                topic=word.get(
                    "topic",
                    "general"
                )
            )

            db.add(
                pending_word
            )

            saved += 1

        db.commit()

        return saved

    except Exception as e:

        db.rollback()

        print(
            f"PENDING SAVE ERROR: {e}"
        )

        return 0

    finally:

        db.close()


def get_pending_words(
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
            return []

        return (
            db.query(PendingWord)
            .filter(
                PendingWord.user_id == user.id
            )
            .order_by(
                PendingWord.id
            )
            .all()
        )

    finally:

        db.close()


def get_pending_word(
    pending_word_id: int
):

    db = SessionLocal()

    try:

        return (
            db.query(PendingWord)
            .filter(
                PendingWord.id == pending_word_id
            )
            .first()
        )

    finally:

        db.close()
