import json

from pathlib import Path


GRAMMAR_FILE = (
    Path(__file__).parent.parent
    / "grammar"
    / "grammar.json"
)


def load_grammar():

    with open(
        GRAMMAR_FILE,
        encoding="utf-8"
    ) as f:

        return json.load(f)
