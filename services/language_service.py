from db.database import SessionLocal
from db.models import User


def get_learning_language(
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
            return "tr"

        return (
            user.learning_language
            or "tr"
        )

    finally:

        db.close()
