import json
import re
from google import genai

from config import GEMINI_API_KEY

from services.ai_cache_service import (
    get_cached_response,
    save_cached_response
)


client = genai.Client(
    api_key=GEMINI_API_KEY
)


MODELS = [
    "gemini-flash-lite-latest",
    "gemini-flash-latest"
]

def generate_story(
    topic: str,
    words: list
) -> str:

    prompt = f"""
Ты опытный преподаватель турецкого языка.

Тема истории: {topic}

Напиши короткую историю уровня A1-A2 на 5-7 предложений.

Используй как можно больше слов из списка:

{', '.join(words)}

Главный приоритет — естественная, логичная и реалистичная история.

Требования:

- История должна описывать одну жизненную ситуацию.
- У истории должно быть начало, развитие и завершение.
- Все события должны быть логически связаны между собой.
- Главный герой должен быть один.
- История должна происходить в рамках темы "{topic}".
- Можно изменять форму слов по правилам турецкого языка.
- Используй грамматически правильные турецкие формы слов.
- Соблюдай правила гармонии гласных и чередования согласных.
- Используй естественные формы слов вместо инфинитивов.
- Используй как можно больше слов из списка, но не жертвуй естественностью текста.
- Выделяй использованные слова тегами <b></b>.
- Не используй Markdown (**).
- Не делай грамматический разбор.
- Не объясняй правила.
- Не добавляй комментарии.
- Не добавляй вступление или заключение.

После истории обязательно добавь полный перевод на русский язык.

Требования к переводу:

- Перевод должен быть только на русском языке.
- Не повторяй турецкий текст.
- Переведи весь рассказ полностью.

Строго соблюдай формат:

🇹🇷 Hikâye

(история на турецком)

🇷🇺 Перевод

(полный перевод на русский)

Ответ должен содержать только эти два блока.
"""

    last_error = None

    for model in MODELS:

        try:

            print(
                f"Trying story model: {model}"
            )

            response = client.models.generate_content(
                model=model,
                contents=prompt
            )

            return response.text

        except Exception as e:

            print(
                f"Story model failed: {model}"
            )

            print(
                str(e)
            )

            last_error = e

            error_text = str(
                e
            ).lower()

            if (
                "429" in error_text
                or "quota" in error_text
                or "resource_exhausted" in error_text
                or "rate limit" in error_text
                or "503" in error_text
                or "unavailable" in error_text
            ):

                continue

            break

    return (
        "⚠️ Не удалось создать историю.\n\n"
        f"{last_error}"
    )

def explain_phrase(
    phrase: str
) -> str:

    cached = get_cached_response(
        phrase
    )

    if cached:

        print(
            f"AI CACHE HIT: {phrase}"
        )

        return cached

    print(
        f"AI CACHE MISS: {phrase}"
    )

    prompt = f"""
Ты опытный преподаватель турецкого языка.

Разбери следующую турецкую фразу:

{phrase}

Отвечай на русском языке.

ВАЖНО:

- Форматируй ответ для Telegram HTML.
- Используй только теги <b> и <i>.
- Не используй Markdown (** или *).
- Не добавляй приветствия, заключения или комментарии.
- Отвечай строго по шаблону ниже.

Шаблон ответа:

🇹🇷 <b>Фраза</b>
(турецкая фраза)

🇷🇺 <b>Перевод</b>
(естественный перевод на русский)

📚 <b>Разбор слов</b>
• <b>слово</b> — объяснение
• <b>слово</b> — объяснение

📖 <b>Грамматика</b>
(краткое объяснение грамматики простым языком)

💡 <b>Пример</b>
🇹🇷 <b>(пример на турецком)</b>
🇷🇺 (перевод примера)
"""

    last_error = None

    for model in MODELS:

        try:

            print(
                f"Trying model: {model}"
            )

            response = client.models.generate_content(
                model=model,
                contents=prompt
            )

            text = response.text

            save_cached_response(
                phrase,
                text,
                model
            )

            print(
                f"AI CACHE SAVED: {phrase}"
            )

            return text

        except Exception as e:

            print(
                f"Model failed: {model}"
            )

            print(
                str(e)
            )

            last_error = e

            error_text = str(
                e
            ).lower()

            if (
                "429" in error_text
                or "quota" in error_text
                or "resource_exhausted" in error_text
                or "rate limit" in error_text
                or "503" in error_text
                or "unavailable" in error_text
            ):

                continue

            break

    return (
        "⚠️ AI временно недоступен.\n\n"
        f"{last_error}"
    )

def extract_new_words(
    story_text: str,
    known_words: list
) -> list:

    prompt = f"""
Ты преподаватель турецкого языка.

Проанализируй историю.

Найди максимум 3 новых полезных турецких слова уровня A1-A2,
которые могут быть полезны для изучения.

ВАЖНО:

- Возвращай только отдельные слова.
- Не возвращай словосочетания.
- Не возвращай выражения из нескольких слов.
- Не возвращай предложения.
- Не возвращай устойчивые фразы.
- Если слово состоит из нескольких слов — пропусти его.
- Каждое значение поля lemma должно содержать только одно слово.

Правила для lemma:

- Для существительных возвращай форму единственного числа.
- Для прилагательных возвращай словарную форму.
- Для глаголов возвращай инфинитив на -mek или -mak.
- Не возвращай формы глаголов из текста.
- Не возвращай слова с окончаниями падежей или личными окончаниями.

Не возвращай следующие слова, потому что они уже известны пользователю:

{", ".join(known_words)}

Для каждого слова укажи:

- lemma
- translation
- topic

Допустимые значения topic:

food
restaurant
transport
travel
hotel
shopping
family
work
city
health
general

Верни ТОЛЬКО JSON.

Формат:

[
  {{
    "lemma": "lezzetli",
    "translation": "вкусный",
    "topic": "food"
  }}
]

Никакого текста до JSON.
Никакого текста после JSON.

История:

{story_text}
"""

    for model in MODELS:

        try:

            response = client.models.generate_content(
                model=model,
                contents=prompt
            )

            text = response.text.strip()

            text = re.sub(
                r"^```json\s*",
                "",
                text
            )

            text = re.sub(
                r"\s*```$",
                "",
                text
            )

            return json.loads(
                text
            )

        except Exception as e:

            print(
                f"NEW WORDS ERROR ({model}): {e}"
            )

            continue

    return []
