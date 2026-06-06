from db.database import (
    SessionLocal
)

from db.models import (
    AICache
)


def get_cached_response(
    phrase: str
):

    db = SessionLocal()

    try:

        record = (
            db.query(
                AICache
            )
            .filter(
                AICache.phrase == phrase
            )
            .first()
        )

        if record:

            return record.response

        return None

    finally:

        db.close()


def save_cached_response(
    phrase: str,
    response: str
):

    db = SessionLocal()

    try:

        exists = (
            db.query(
                AICache
            )
            .filter(
                AICache.phrase == phrase
            )
            .first()
        )

        if exists:

            return

        db.add(
            AICache(
                phrase=phrase,
                response=response
            )
        )

        db.commit()

    finally:

        db.close()
