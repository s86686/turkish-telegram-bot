import json


def load_dictionary():
    with open(
        "data/turkish_dictionary.json",
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)


def get_first_word():
    words = load_dictionary()

    if not words:
        return None

    return words[0]
