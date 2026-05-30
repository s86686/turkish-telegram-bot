import json
import random


def load_dictionary():

    with open(
        "data/turkish_dictionary.json",
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


def get_random_word():

    words = load_dictionary()

    return random.choice(words)
