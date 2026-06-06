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
    words: list
) -> str:

    prompt = f"""
Ты опытный преподаватель турецкого языка.

Напиши короткую историю уровня A1-A2 на 4-5 предложений.

Используй ВСЕ следующие слова:

{', '.join(words)}

Требования:

- История должна быть естественной и похожей на реальную жизненную ситуацию.
- Все предложения должны быть логически связаны между собой.
- Можно изменять форму слов по правилам турецкого языка.
- Используй естественные формы слов вместо инфинитивов.

Примеры:
- istemek → istedi / istiyorum / istedik
- dinlemek → dinledim / dinliyorum
- önermek → önerdi / öneriyorum

- Каждое слово из списка должно быть использовано хотя бы один раз.
- Выделяй использованные слова тегами <b></b>.
- Не используй Markdown (**).
- Не делай грамматический разбор.
- Не объясняй правила.
- Не добавляй комментарии.
- Не добавляй вступления и заключения.

Перевод:

- После истории обязательно сделай полный перевод на русский язык.
- Перевод должен быть только на русском языке.
- Не повторяй турецкий текст в блоке перевода.

Строго соблюдай формат:

📖 Hikaye

(история на турецком)

🇷🇺 Çeviri

(полный перевод на русский)

Ответ должен содержать только эти два блока и ничего больше.
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
