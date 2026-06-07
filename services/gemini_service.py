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
Ты преподаватель турецкого языка.

Разбери турецкую фразу.

Покажи:

1. Перевод
2. Разбор слов
3. Краткое объяснение грамматики
4. Один пример использования

Отвечай на русском языке.

Фраза:

{phrase}
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
