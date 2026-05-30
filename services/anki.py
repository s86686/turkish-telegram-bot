def quality_to_text(
    quality: int
):

    mapping = {
        0: "😵 Забыл",
        1: "😕 Трудно",
        2: "🙂 Хорошо",
        3: "😎 Легко"
    }

    return mapping.get(
        quality,
        "Неизвестно"
    )
