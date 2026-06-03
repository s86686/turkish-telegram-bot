from db.database import SessionLocal
from db.models import (
    User,
    Word
)


TOPIC_NAMES = {
    "general": "📚 Общие слова",
    "transport": "🚌 Транспорт",
    "hotel": "🏨 Отель",
    "pharmacy": "💊 Аптека",
    "restaurant": "🍽 Ресторан",
    "cafe": "☕ Кафе",
    "market": "🧺 Базар",
    "shop": "🛒 Магазин",
    "beach": "🏖 Пляж",
    "airport": "✈️ Аэропорт",
    "excursions": "🏛 Экскурсии",
    "emergency": "🚨 Экстренные ситуации",
    "social": "🤝 Общение",
    "family": "👨‍👩‍👧‍👦 Семья",
    "people": "👥 Люди",
    "food": "🍎 Еда",
    "education": "🎓 Образование",
    "home": "🏠 Дом"
}


def get_topic_name(
    topic: str
):

    return TOPIC_NAMES.get(
        topic,
        f"📚 {topic.replace('_', ' ').title()}"
    )


def get_topics():

    db = SessionLocal()

    try:

        rows = (
            db.query(
                Word.topic
            )
            .distinct()
            .order_by(
                Word.topic
            )
            .all()
        )

        return [
            row[0]
            for row in rows
            if row[0]
        ]

    finally:

        db.close()


def set_user_topic(
    telegram_id: int,
    topic: str
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

        user.selected_topic = topic

        db.commit()

    finally:

        db.close()


def get_user_topic(
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
            return "all"

        return (
            user.selected_topic
            or "all"
        )

    finally:

        db.close()
