from aiogram import Router

from aiogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    FSInputFile
)

from services.tts_service import (
    generate_tts
)

from services.dialog_service import (
    load_all_dialogs
)

from services.gemini_service import (
    explain_phrase
)

router = Router()

VOICE_MESSAGES = {}

WORDS_MESSAGES = {}

SPEAK_IN_PROGRESS = set()

AI_IN_PROGRESS = set()

AI_MESSAGES = {}

DIALOG_SETS = load_all_dialogs()

print(
    f"Topics loaded: {list(DIALOG_SETS.keys())}"
)


topics_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="☕ Кафе",
                callback_data="dialog_cafe"
            )
        ],
        [
            InlineKeyboardButton(
                text="🍽 Ресторан",
                callback_data="dialog_restaurant"
            )
        ],
        [
            InlineKeyboardButton(
                text="🚌 Транспорт",
                callback_data="dialog_transport"
            )
        ],
        [
            InlineKeyboardButton(
                text="🛒 Магазин",
                callback_data="dialog_shop"
            )
        ],
        [
            InlineKeyboardButton(
                text="🧺 Базар",
                callback_data="dialog_bazaar"
            )
        ],
        [
            InlineKeyboardButton(
                text="🏨 Отель",
                callback_data="dialog_hotel"
            )
        ],
        [
            InlineKeyboardButton(
                text="💊 Аптека",
                callback_data="dialog_pharmacy"
            )
        ],
        [
            InlineKeyboardButton(
                text="🏖 Пляж",
                callback_data="dialog_beach"
            )
        ],
        [
            InlineKeyboardButton(
                text="🏛 Экскурсии и достопримечательности",
                callback_data="dialog_excursions"
            )
        ],
        [
            InlineKeyboardButton(
                text="🤝 Знакомство и общение",
                callback_data="dialog_social"
            )
        ],
        [
            InlineKeyboardButton(
                text="🚨 Экстренные ситуации",
                callback_data="dialog_emergency"
            )
        ],
        [
            InlineKeyboardButton(
                text="✈️ Аэропорт",
                callback_data="dialog_airport"
            )
        ]
    ]
)

async def delete_ai_message(callback: CallbackQuery):
    """Удаляет предыдущий AI разбор с экрана"""
    user_id = callback.from_user.id
    message_id = AI_MESSAGES.get(user_id)
    if message_id:
        try:
            await callback.bot.delete_message(
                chat_id=callback.message.chat.id,
                message_id=message_id
            )
        except Exception:
            pass
        AI_MESSAGES.pop(user_id, None)

async def delete_dialog_voice(
    callback: CallbackQuery
):

    voice_message_id = VOICE_MESSAGES.get(
        callback.from_user.id
    )

    if not voice_message_id:
        return

    try:

        await callback.bot.delete_message(
            chat_id=callback.message.chat.id,
            message_id=voice_message_id
        )

    except Exception:
        pass

    VOICE_MESSAGES.pop(
        callback.from_user.id,
        None
    )

async def delete_words_message(
    callback: CallbackQuery
):

    words_message_id = WORDS_MESSAGES.get(
        callback.from_user.id
    )

    if not words_message_id:
        return

    try:

        await callback.bot.delete_message(
            chat_id=callback.message.chat.id,
            message_id=words_message_id
        )

    except Exception:
        pass

    WORDS_MESSAGES.pop(
        callback.from_user.id,
        None
    )
    
def dialog_keyboard(
    topic: str,
    dialog_index: int
):

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔊 Озвучить диалог",
                    callback_data=f"dialog_speak_{topic}_{dialog_index}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📚 Ключевые слова",
                    callback_data=f"dialog_words_{topic}_{dialog_index}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔍 Разобрать фразу",
                    callback_data=f"dialog_ai_{topic}_{dialog_index}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="➡️ Следующий диалог",
                    callback_data=f"dialog_next_{topic}_{dialog_index}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад к темам",
                    callback_data="dialogs_menu"
                )
            ]
        ]
    )


def build_dialog_text(
    dialog
):

    text = (
        f"🎭 {dialog['title']}\n\n"
    )

    for line in dialog["lines"]:

        speaker = {
            "Garson": "👨‍🍳 Garson",
            "Şoför": "🚌 Şoför",
            "Yerli": "👤 Yerli",
            "Siz": "👤 Siz",
            "Satıcı": "🛍️ Satıcı",
            "Resepsiyonist": "🏨 Resepsiyonist",
            "Doktor": "👨‍⚕️ Doktor",
            "Eczacı": "💊 Eczacı",
            "Polis": "👮 Polis",
            "Görevli": "ℹ️ Görevli"
        }.get(
            line["speaker"],
            f"👤 {line['speaker']}"
        )

        text += (
            f"{speaker}\n"
            f"🇹🇷 {line['tr']}\n"
            f"🇷🇺 {line['ru']}\n\n"
        )

    return text


@router.message(
    lambda m: m.text == "🎭 Диалоги"
)
async def dialogs_menu(
    message: Message
):

    await message.answer(
        "🎭 Выберите тему:",
        reply_markup=topics_keyboard
    )


@router.callback_query(
    lambda c: c.data == "dialogs_menu"
)
async def back_to_dialogs_menu(
    callback: CallbackQuery
):

    await delete_dialog_voice(
        callback
    )

    await delete_words_message(
        callback
    )

    await delete_ai_message(
        callback
    )

    await callback.message.edit_text(
        "🎭 Выберите тему:",
        reply_markup=topics_keyboard
    )

    await callback.answer()


@router.callback_query(
    lambda c: c.data.startswith(
        "dialog_"
    )
    and c.data.count("_") == 1
)
async def show_dialog_topic(
    callback: CallbackQuery
):

    topic = callback.data.replace(
        "dialog_",
        ""
    )

    if topic not in DIALOG_SETS:

        await callback.answer(
            "🚧 Диалоги скоро появятся",
            show_alert=True
        )

        return

    await delete_dialog_voice(
        callback
    )

    await delete_words_message(
        callback
    )

    await delete_ai_message(
        callback
    )

    dialog = DIALOG_SETS[
        topic
    ][0]

    await callback.message.edit_text(
        build_dialog_text(
            dialog
        ),
        reply_markup=dialog_keyboard(
            topic,
            0
        )
    )

    await callback.answer()


@router.callback_query(
    lambda c: c.data.startswith(
        "dialog_next_"
    )
)
async def next_dialog(
    callback: CallbackQuery
):

    await delete_dialog_voice(
        callback
    )

    await delete_words_message(
        callback
    )

    await delete_ai_message(
        callback
    )

    parts = callback.data.split(
        "_"
    )

    topic = parts[2]

    current_index = int(
        parts[3]
    )

    dialogs = DIALOG_SETS[
        topic
    ]

    next_index = (
        current_index + 1
    ) % len(dialogs)

    dialog = dialogs[
        next_index
    ]

    await callback.message.edit_text(
        build_dialog_text(
            dialog
        ),
        reply_markup=dialog_keyboard(
            topic,
            next_index
        )
    )

    await callback.answer()


@router.callback_query(
    lambda c: c.data.startswith(
        "dialog_speak_"
    )
)
async def speak_dialog(
    callback: CallbackQuery
):

    await callback.answer()

    user_id = callback.from_user.id

    if user_id in SPEAK_IN_PROGRESS:
        return

    SPEAK_IN_PROGRESS.add(
        user_id
    )
    
    parts = callback.data.split(
        "_"
    )

    topic = parts[2]

    dialog_index = int(
        parts[3]
    )

    dialog = DIALOG_SETS[
        topic
    ][dialog_index]

    text = " ".join(
        line["tr"]
        for line in dialog["lines"]
    )

    import os

    filename = await generate_tts(
        text
    )

    try:

        audio = FSInputFile(
            filename
        )

        voice_msg = await callback.message.answer_voice(
            audio
        )

        VOICE_MESSAGES[
            callback.from_user.id
        ] = voice_msg.message_id

    finally:

        if os.path.exists(
            filename
        ):
            os.remove(
                filename
            )

        SPEAK_IN_PROGRESS.discard(
            user_id
        ) 

@router.callback_query(
    lambda c: c.data.startswith(
        "dialog_words_"
    )
)
async def show_dialog_words(
    callback: CallbackQuery
):

    parts = callback.data.split(
        "_"
    )

    topic = parts[2]

    dialog_index = int(
        parts[3]
    )

    dialog = DIALOG_SETS[
        topic
    ][dialog_index]

    vocabulary = dialog.get(
        "vocabulary",
        []
    )

    if not vocabulary:

        await callback.answer(
            "Для этого диалога словарь ещё не заполнен",
            show_alert=True
        )

        return

    await delete_words_message(
        callback
    )

    text = "📚 Ключевые слова\n\n"

    for item in vocabulary:

        text += (
            f"{item['tr']} — {item['ru']}\n"
        )

    msg = await callback.message.answer(
        text
    )

    WORDS_MESSAGES[
        callback.from_user.id
    ] = msg.message_id

    await callback.answer()

@router.callback_query(lambda c: c.data.startswith("dialog_ai_"))
async def explain_dialog_phrase(callback: CallbackQuery):
    user_id = callback.from_user.id

    # защита от параллельных запросов
    if user_id in AI_IN_PROGRESS:
        await callback.answer("Подождите завершения предыдущего запроса")
        return
    AI_IN_PROGRESS.add(user_id)

    await delete_ai_message(callback)  # удаляем предыдущий разбор

    try:
        parts = callback.data.split("_")
        topic = parts[2]
        dialog_index = int(parts[3])
        dialog = DIALOG_SETS[topic][dialog_index]

        phrase = dialog.get("ai_phrase") or dialog["lines"][-1]["tr"]

        wait_msg = await callback.message.answer("🤖 Анализирую фразу...")

        result_html = explain_phrase(phrase)

        # сохраняем message_id для последующего удаления
        AI_MESSAGES[user_id] = wait_msg.message_id

        await wait_msg.edit_text(
            f"🔍 Фраза\n\n<b>{phrase}</b>\n\n{result_html}",
            parse_mode=ParseMode.HTML
        )
        await callback.answer()

    except Exception as e:
        await wait_msg.edit_text(f"Ошибка AI:\n{e}")
    finally:
        AI_IN_PROGRESS.discard(user_id)

