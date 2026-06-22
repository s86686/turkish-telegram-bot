FEATURE_NOT_AVAILABLE_MESSAGE = {
    "daily_story": (
        "🔒 История дня пока доступна только "
        "для турецкого языка."
    ),
    "dialogs": (
        "🔒 Диалоги пока доступны "
        "только для турецкого языка."
    )
}


def is_feature_available(
    user,
    feature: str
) -> bool:

    if (
        user.learning_language == "en"
        and feature in {
            "daily_story",
            "dialogs"
        }
    ):
        return False

    return True


def get_feature_message(
    feature: str
) -> str:

    return FEATURE_NOT_AVAILABLE_MESSAGE.get(
        feature,
        "🔒 Функция недоступна."
    )
