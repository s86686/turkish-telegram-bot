from db.database import SessionLocal

from db.models import User


def set_direction(
    telegram_id,
    direction
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

        user.quiz_direction = direction

        db.commit()

    finally:

        db.close()


def get_direction(
    telegram_id
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
            return "TR_RU"

        return (
            user.quiz_direction
            or "TR_RU"
        )

    finally:

        db.close()
