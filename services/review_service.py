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

if quality == 0:

    user_word.repetitions = 0
    user_word.interval_days = 1

elif quality == 1:

    user_word.repetitions = max(
        0,
        (user_word.repetitions or 0) - 1
    )

    user_word.interval_days = 2

elif quality == 2:

    user_word.repetitions = (
        user_word.repetitions or 0
    ) + 1

    if user_word.repetitions == 1:
        user_word.interval_days = 3
    elif user_word.repetitions == 2:
        user_word.interval_days = 7
    else:
        user_word.interval_days = int(
            user_word.interval_days * 1.8
        )

elif quality == 3:

    user_word.repetitions = (
        user_word.repetitions or 0
    ) + 1

    if user_word.repetitions == 1:
        user_word.interval_days = 5
    elif user_word.repetitions == 2:
        user_word.interval_days = 14
    else:
        user_word.interval_days = int(
            user_word.interval_days * 2.5
        )

user_word.next_review = (
    datetime.utcnow()
    + timedelta(
        days=user_word.interval_days
    )
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
