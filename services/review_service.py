from datetime import (
    datetime,
    timedelta
)

from db.database import SessionLocal

from db.models import (
    User,
    UserWord
)


def save_review(
    telegram_id: int,
    word_id: int,
    quality: int
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
            return

        user_word = (
            db.query(UserWord)
            .filter(
                UserWord.user_id == user.id,
                UserWord.word_id == word_id
            )
            .first()
        )

        if not user_word:

            user_word = UserWord(
                user_id=user.id,
                word_id=word_id
            )

            db.add(user_word)

        intervals = {
            0: 1,
            1: 2,
            2: 5,
            3: 10
        }

        interval = intervals.get(
            quality,
            1
        )

        user_word.interval_days = interval

        user_word.next_review = (
            datetime.utcnow()
            + timedelta(days=interval)
        )

        if quality >= 2:

            user_word.correct_count = (
                user_word.correct_count or 0
            ) + 1

        else:
            user_word.wrong_count = (
                user_word.wrong_count or 0
            ) + 1

        db.commit()

    finally:
        db.close()
