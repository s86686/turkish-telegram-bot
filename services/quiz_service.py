import random


def build_quiz(
    current_word,
    all_words,
    direction="TR_RU"
):

    if direction == "RU_TR":

        correct = (
            current_word["lemma"]
        )

        wrong_answers = [

            word["lemma"]

            for word in all_words

            if word["id"]
            != current_word["id"]
        ]

        question = (
            current_word["translation"]
        )

    else:

        correct = (
            current_word["translation"]
        )

        wrong_answers = [

            word["translation"]

            for word in all_words

            if word["id"]
            != current_word["id"]
        ]

        question = (
            current_word["lemma"]
        )

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
        "question": question,
        "options": options,
        "correct":
            options.index(
                correct
            )
    }
