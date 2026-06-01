# services/dialog_service.py

import json

from pathlib import Path


DIALOGS_DIR = (
    Path(__file__).parent.parent
    / "dialogs"
)


def load_dialogs(
    filename: str
):

    filepath = (
        DIALOGS_DIR
        / filename
    )

    with open(
        filepath,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(
            f
        )


def load_all_dialogs():

    dialogs = {}

    if not DIALOGS_DIR.exists():

        return dialogs

    for filepath in DIALOGS_DIR.glob(
        "*.json"
    ):

        try:

            with open(
                filepath,
                "r",
                encoding="utf-8"
            ) as f:

                dialogs[
                    filepath.stem
                ] = json.load(
                    f
                )

            print(
                f"Loaded dialogs: {filepath.name}"
            )

        except Exception as e:

            print(
                f"Error loading {filepath.name}: {e}"
            )

    return dialogs
