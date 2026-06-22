from aiogram import Router
from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)
from aiogram.enums import ParseMode

from services.daily_story_service import (
    get_daily_story,
    get_user_words_for_story,
    create_daily_story,
    filter_unknown_words
)

from services.gemini_service import (
    extract_new_words,
    generate_word_card
)

from services.pending_words_service import (
    save_pending_words,
    get_pending_words,
    get_pending_word,
    add_pending_word_to_dictionary,
    save_pending_word_card
)

from services.users import (
    get_user_by_telegram_id
)

from services.access_service import (
    is_feature_available,
    FEATURE_NOT_AVAILABLE_MESSAGE
)

router = Router()

daily_story_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="❌ Закрыть",
                callback_data="close_story"
            )
        ]
    ]
)


def build_pending_words_keyboard(
    pending_words
):

    keyboard = []

    for word in pending_words:

        keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"➕ {word.lemma}",
                    callback_data=f"pending_word_{word.id}"
                )
            ]
        )

    keyboard.append(
        [
            InlineKeyboardButton(
                text="❌ Закрыть",
                callback_data="close_story"
            )
        ]
    )

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )

def build_word_confirm_keyboard(
    pending_word_id: int
):

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Добавить в словарь",
                    callback_data=f"confirm_word_{pending_word_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Отмена",
                    callback_data="cancel_word"
                )
            ]
        ]
    )

@router.message(
    lambda m: m.text == "📖 История дня"
)
async def show_daily_story(
    message: Message
):

    user_id = message.from_user.id

    user = get_user_by_telegram_id(
        user_id
    )

    if not user:

        await message.answer(
            "Пользователь не найден."
        )

        return

    if not is_feature_available(
        user,
        "daily_story"
    ):

        await message.answer(
            FEATURE_NOT_AVAILABLE_MESSAGE
        )

        return

    # История уже существует
    story = get_daily_story(
        user_id
    )

    if story:

        pending_words = get_pending_words(
            user_id
        )

        keyboard = build_pending_words_keyboard(
            pending_words
        )

        await message.answer(
            story.story_text,
            reply_markup=keyboard,
            parse_mode=ParseMode.HTML
        )

        return

    # Создаем новую историю
    topic, words = get_user_words_for_story(
        user_id
    )

    if not words:

        await message.answer(
            "Сегодня ещё нет изученных слов для истории."
        )

        return

    story = create_daily_story(
        user_id,
        topic,
        words
    )

    if not story or not story.story_text:

        await message.answer(
            "⚠️ Не удалось сгенерировать историю. Попробуйте позже."
        )

        return

    new_words = extract_new_words(
        story.story_text,
        words
    )

    story.story_text += (
        f"\n\nDEBUG BEFORE FILTER:\n{new_words}"
    )

    new_words = filter_unknown_words(
        new_words
    )

    story.story_text += (
        f"\n\nDEBUG AFTER FILTER:\n{new_words}"
    )

    saved_words = save_pending_words(
        telegram_id=user_id,
        language="tr",
        words=new_words
    )

    story.story_text += (
        f"\n\nDEBUG PENDING SAVED: "
        f"{saved_words}"
    )

    pending_words = get_pending_words(
        user_id
    )

    if pending_words:

        words_text = (
            "\n\n🆕 Новые слова из истории:\n\n"
        )

        for word in pending_words:

            words_text += (
                f"• {word.lemma} — "
                f"{word.translation}\n"
            )

        story.story_text += words_text

    keyboard = build_pending_words_keyboard(
        pending_words
    )

    await message.answer(
        story.story_text,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )


@router.callback_query(
    lambda c: c.data.startswith(
        "pending_word_"
    )
)
async def pending_word_clicked(
    callback: CallbackQuery
):

    pending_word_id = int(
        callback.data.replace(
            "pending_word_",
            ""
        )
    )

    word = get_pending_word(
        pending_word_id
    )

    if not word:

        await callback.answer(
            "Слово не найдено",
            show_alert=True
        )

        return

    await callback.answer(
        "Генерирую карточку..."
    )

    card = generate_word_card(
        lemma=word.lemma,
        translation=word.translation,
        topic=word.topic,
        language=word.language
    )
    
    if not card:
    
        await callback.message.answer(
            "⚠️ Не удалось создать карточку слова."
        )
    
        return
    
    save_pending_word_card(
        pending_word_id,
        card
    )
    example = (
        card.get("example_foreign")
        or card.get("example_tr")
        or card.get("example_en")
        or ""
    )

    language_flag = (
        "🇹🇷"
        if word.language == "tr"
        else "🇬🇧"
    )

    text = (
        f"📖 <b>{card['lemma']}</b>\n\n"
        f"🇷🇺 {card['translation']}\n"
        f"🏷 Тема: {card['topic']}\n"
        f"📊 Уровень: {card['level']}\n\n"
        f"📌 <b>Пример</b>\n\n"
        f"{language_flag} {example}\n\n"
        f"🇷🇺 {card['example_ru']}"
    )

    await callback.message.answer(
        text,
        reply_markup=build_word_confirm_keyboard(
            pending_word_id
        ),
        parse_mode=ParseMode.HTML
    )


@router.callback_query(
    lambda c: c.data.startswith(
        "confirm_word_"
    )
)
async def confirm_word(
    callback: CallbackQuery
):

    pending_word_id = int(
        callback.data.replace(
            "confirm_word_",
            ""
        )
    )

    word = get_pending_word(
        pending_word_id
    )

    if not word:

        await callback.answer(
            "Слово не найдено",
            show_alert=True
        )

        return

    if not word.card_json:

        await callback.message.answer(
            "⚠️ Карточка слова не найдена."
        )

        return

    try:

        import json
    
        card = json.loads(
            word.card_json or "{}"
        )
    
    except Exception:
    
        await callback.message.answer(
            "⚠️ Ошибка чтения карточки слова."
        )
    
        return
    
    if not card:
    
        await callback.message.answer(
            "⚠️ Карточка слова пуста."
        )
    
        return

    success, result = (
        add_pending_word_to_dictionary(
            pending_word_id,
            card
        )
    )

    if success:

        await callback.message.answer(
            f"✅ Слово добавлено в словарь\n\n"
            f"📖 {result}"
        )

    else:

        await callback.message.answer(
            f"❌ Ошибка\n\n{result}"
        )

    await callback.answer()

@router.callback_query(
    lambda c: c.data == "cancel_word"
)
async def cancel_word(
    callback: CallbackQuery
):

    try:

        await callback.message.delete()

    except Exception:

        pass

    await callback.answer()


@router.callback_query(
    lambda c: c.data == "close_story"
)
async def close_story(
    callback: CallbackQuery
):

    try:

        await callback.message.delete()

    except Exception:

        pass

    await callback.answer()
