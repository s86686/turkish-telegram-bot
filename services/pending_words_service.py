from db.database import SessionLocal
from db.models import (
    User,
    PendingWord,
    Word,
    EnglishWord,
    UserWord,
    UserEnglishWord
)

import json

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

def add_pending_word_to_dictionary(
    pending_word_id: int,
    card: dict
):

    db = SessionLocal()

    try:

        pending_word = (
            db.query(PendingWord)
            .filter(
                PendingWord.id == pending_word_id
            )
            .first()
        )

        if not pending_word:

            return (
                False,
                "PendingWord not found"
            )

        if pending_word.language == "tr":

            word = (
                db.query(Word)
                .filter(
                    Word.lemma == card["lemma"]
                )
                .first()
            )

            if not word:

                word = Word(
                    lemma=card["lemma"],
                    translation=card["translation"],
                    level=card["level"],
                    topic=card["topic"],
                    example_tr=card.get(
                        "example_foreign"
                    ),
                    example_ru=card.get(
                        "example_ru"
                    ),
                    priority=100
                )

                db.add(word)
                db.flush()

            existing_user_word = (
                db.query(UserWord)
                .filter(
                    UserWord.user_id == pending_word.user_id,
                    UserWord.word_id == word.id
                )
                .first()
            )

            if not existing_user_word:

                db.add(
                    UserWord(
                        user_id=pending_word.user_id,
                        word_id=word.id
                    )
                )

        else:

            word = (
                db.query(EnglishWord)
                .filter(
                    EnglishWord.lemma == card["lemma"]
                )
                .first()
            )

            if not word:

                word = EnglishWord(
                    lemma=card["lemma"],
                    translation=card["translation"],
                    level=card["level"],
                    topic=card["topic"],
                    example_en=card.get(
                        "example_foreign"
                    ),
                    example_ru=card.get(
                        "example_ru"
                    ),
                    priority=100
                )

                db.add(word)
                db.flush()

            existing_user_word = (
                db.query(UserEnglishWord)
                .filter(
                    UserEnglishWord.user_id == pending_word.user_id,
                    UserEnglishWord.word_id == word.id
                )
                .first()
            )

            if not existing_user_word:

                db.add(
                    UserEnglishWord(
                        user_id=pending_word.user_id,
                        word_id=word.id
                    )
                )

        db.delete(
            pending_word
        )

        db.commit()

        return (
            True,
            card["lemma"]
        )

    except Exception as e:

        db.rollback()

        print(
            f"ADD WORD ERROR: {e}"
        )

        return (
            False,
            str(e)
        )

    finally:

        db.close()

def save_pending_word_card(
    pending_word_id: int,
    card: dict
):

    db = SessionLocal()

    try:

        pending_word = (
            db.query(PendingWord)
            .filter(
                PendingWord.id == pending_word_id
            )
            .first()
        )

        if not pending_word:
            return False

        pending_word.card_json = json.dumps(
            card,
            ensure_ascii=False
        )

        db.commit()

        return True

    except Exception as e:

        db.rollback()

        print(
            f"SAVE CARD ERROR: {e}"
        )

        return False

    finally:

        db.close()
