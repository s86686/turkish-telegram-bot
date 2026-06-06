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
Ты преподаватель турецкого языка.

Напиши короткую историю уровня A1-A2 на 4-5 предложений. История должна быть естественной, как в живой речи, простой для понимания.

Используй все эти слова:

{', '.join(words)}

Требования:

- Можно изменять форму слов по правилам турецкого языка, чтобы история звучала естественно.
  Например: 
    - istemek → istiyorum / istedi / istedik
    - dinlemek → dinliyorum / dinledim
    - önermek → önerdi / öneriyorum
- История должна включать простые бытовые ситуации, как в реальной жизни.
- После истории обязательно добавь перевод на русский язык.
- Не делай разбор слов и грамматический анализ.
- ОТВЕТ ДОЛЖЕН СОДЕРЖАТЬ ТОЛЬКО ДВА БЛОКА:
  1) Турецкий текст с выделением использованных слов жирным.
  2) Перевод на русский.

ФОРМАТ ВЫВОДА (обязательно соблюдай этот шаблон):

📖 Hikaye
(сюжет на турецком, выделяя использованные слова жирным)

🇷🇺 Çeviri
(перевод на русский)

Ничего лишнего. Не добавляй заголовки, пояснения, инструкции, разбор грамматики или списки слов.
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
