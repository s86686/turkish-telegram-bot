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

            print(
                f"CACHE HIT: {phrase}"
            )

            return record.response

        print(
            f"CACHE MISS: {phrase}"
        )

        return None

    finally:

        db.close()


def save_cached_response(
    phrase: str,
    response: str,
    model_name: str
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
                response=response,
                model_name=model_name
            )
        )

        db.commit()

        print(
            f"CACHE SAVED: {phrase}"
        )

    finally:

        db.close()
