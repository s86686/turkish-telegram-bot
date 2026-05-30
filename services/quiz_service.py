import random


def build_quiz(
    current_word,
    all_words
):

    correct = (
        current_word["translation"]
    )

    wrong_answers = [

        word["translation"]

        for word in all_words

        if word["id"]
        != current_word["id"]
    ]

    options = random.sample(
        wrong_answers,
        min(
            3,
            len(wrong_answers)
        )
    )

    options.append(
        correct
    )

    random.shuffle(
        options
    )

    return {
        "options": options,
        "correct":
            options.index(
                correct
            )
    }
