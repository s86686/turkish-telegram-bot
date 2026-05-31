from aiogram import Router
from aiogram.types import Message

from services.stats_service import (
    get_stats
)

router = Router()


@router.message(
    lambda m: m.text ==
    "📈 Статистика"
)
async def stats(
    message: Message
):

    data = get_stats(
        message.from_user.id
    )

    if not data:

        await message.answer(
            "Нет данных."
        )

        return

    total = (
        data["correct"]
        + data["wrong"]
    )

    accuracy = 0

    if total > 0:

        accuracy = round(
            data["correct"]
            / total * 100,
            1
        )

    await message.answer(

        f"📈 Статистика\n\n"
    
        f"📚 Изучено слов: "
        f"{data['learned']}\n\n"
    
        f"🆕 Сегодня изучено: "
        f"{data['learned_today']} / "
        f"{data['daily_limit']}\n\n"
    
        f"🔁 К повторению: "
        f"{data['review_today']}\n\n"
    
        f"📦 Осталось новых слов: "
        f"{data['new_words']}\n\n"
    
        f"🎯 Точность: "
        f"{accuracy}%\n\n"
    
        f"✅ Правильных ответов: "
        f"{data['correct']}\n"
    
        f"❌ Ошибок: "
        f"{data['wrong']}"
    )
