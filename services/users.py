from db.database import SessionLocal
from db.models import User


def get_user_by_telegram_id(
    telegram_id: int
):
    db = SessionLocal()

    try:
        return (
            db.query(User)
            .filter(
                User.telegram_id == telegram_id
            )
            .first()
        )
    finally:
        db.close()


def create_user(
    telegram_id: int,
    username: str | None
):
    db = SessionLocal()

    try:

        user = User(
            telegram_id=telegram_id,
            username=username
        )

        db.add(user)

        db.commit()

        db.refresh(user)

        return user

    finally:
        db.close()


def get_or_create_user(
    telegram_id: int,
    username: str | None
):
    user = get_user_by_telegram_id(
        telegram_id
    )

    if user:
        return user

    return create_user(
        telegram_id,
        username
    )
