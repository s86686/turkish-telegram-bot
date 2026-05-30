from db.database import SessionLocal
from db.models import User


def get_or_create_user(
    telegram_id,
    username
):
    session = SessionLocal()

    user = (
        session.query(User)
        .filter(
            User.telegram_id == telegram_id
        )
        .first()
    )

    if user:
        session.close()
        return user

    user = User(
        telegram_id=telegram_id,
        username=username
    )

    session.add(user)
    session.commit()

    session.refresh(user)

    session.close()

    return user
