from aiogram import Router

from aiogram.types import (
    Message
)

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton
)

from dialogs.cafe import (
    CAFE_DIALOGS
)

router = Router()


@router.message(
    lambda m: m.text == "☕ Кафе"
)
async def cafe_dialogs(
    message: Message
):

    dialog = CAFE_DIALOGS[0]

    text = (
        f"🎭 {dialog['title']}\n\n"
    )

    for line in dialog["lines"]:

        text += (
            f"👤 {line['speaker']}\n"
            f"{line['tr']}\n"
            f"{line['ru']}\n\n"
        )

    await message.answer(
        text
    )
