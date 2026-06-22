FEATURE_NOT_AVAILABLE_MESSAGE = (
    "🔒 История дня пока доступна только "
    "для турецкого языка.\n\n"
    "Для английского языка сейчас доступны:\n"
    "• Новые слова\n"
    "• Повторение слов\n"
    "• Викторина"
)


def is_feature_available(
    user,
    feature: str
) -> bool:

    if (
        user.learning_language == "en"
        and feature == "daily_story"
    ):
        return False

    return True
