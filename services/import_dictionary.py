import json

from db.database import SessionLocal
from db.models import Word


def import_dictionary():

    session = SessionLocal()

    with open(
        "data/turkish_dictionary.json",
        encoding="utf-8"
    ) as f:

        words = json.load(f)

    for item in words:

        exists = (
            session.query(Word)
            .filter(
                Word.id == item["id"]
            )
            .first()
        )

        if exists:
            continue

        word = Word(
            id=item["id"],
            lemma=item["lemma"],
            translation=item["translation"],
            level=item["level"],
            topic=item["topic"],
            frequency_rank=item["frequency_rank"]
        )

        session.add(word)

    session.commit()

    session.close()
