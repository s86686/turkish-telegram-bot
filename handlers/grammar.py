from aiogram import Router
from aiogram.enums import ParseMode

from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from services.grammar_service import (
    load_grammar
)

router = Router()

GRAMMAR = load_grammar()


def grammar_menu_keyboard():

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=lesson["title"],
                    callback_data=f"grammar_{i}"
                )
            ]
            for i, lesson in enumerate(
                GRAMMAR
            )
        ]
    )


def lesson_keyboard(
    index: int
):

    buttons = []

    if index > 0:

        buttons.append(
            InlineKeyboardButton(
                text="⬅️ Предыдущий",
                callback_data=f"grammar_prev_{index}"
            )
        )

    if index < len(GRAMMAR) - 1:

        buttons.append(
            InlineKeyboardButton(
                text="➡️ Следующий",
                callback_data=f"grammar_next_{index}"
            )
        )

    keyboard = []

    if buttons:

        keyboard.append(
            buttons
        )

    keyboard.append(
        [
            InlineKeyboardButton(
                text="📚 Все уроки",
                callback_data="grammar_menu"
            )
        ]
    )

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )


@router.message(
    lambda m: m.text == "📖 Грамматика"
)
async def grammar_menu(
    message: Message
):

    await message.answer(
        "📖 Мини-грамматика\n\nВыберите тему:",
        reply_markup=grammar_menu_keyboard()
    )


@router.callback_query(
    lambda c: c.data == "grammar_menu"
)
async def show_grammar_menu(
    callback: CallbackQuery
):

    await callback.message.edit_text(
        "📖 Мини-грамматика\n\nВыберите тему:",
        reply_markup=grammar_menu_keyboard()
    )

    await callback.answer()


@router.callback_query(
    lambda c: c.data.startswith(
        "grammar_"
    )
    and c.data.count("_") == 1
)
async def show_lesson(
    callback: CallbackQuery
):

    index = int(
        callback.data.split("_")[1]
    )

    lesson = GRAMMAR[index]

    await callback.message.edit_text(
        f"{lesson['title']}\n\n"
        f"{lesson['content']}",
        reply_markup=lesson_keyboard(index),
        parse_mode=ParseMode.HTML
    )

    await callback.answer()


@router.callback_query(
    lambda c: c.data.startswith(
        "grammar_next_"
    )
)
async def next_lesson(
    callback: CallbackQuery
):

    current = int(
        callback.data.split("_")[2]
    )

    index = current + 1

    lesson = GRAMMAR[index]

    await callback.message.edit_text(
        f"{lesson['title']}\n\n"
        f"{lesson['content']}",
        reply_markup=lesson_keyboard(index),
        parse_mode=ParseMode.HTML
    )

    await callback.answer()


@router.callback_query(
    lambda c: c.data.startswith(
        "grammar_prev_"
    )
)
async def prev_lesson(
    callback: CallbackQuery
):

    current = int(
        callback.data.split("_")[2]
    )

    index = current - 1

    lesson = GRAMMAR[index]

    await callback.message.edit_text(
        f"{lesson['title']}\n\n"
        f"{lesson['content']}",
        reply_markup=lesson_keyboard(index),
        parse_mode=ParseMode.HTML
    )

    await callback.answer()
