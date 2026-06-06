from google import genai

from config import GEMINI_API_KEY


client = genai.Client(
    api_key=GEMINI_API_KEY
)


def explain_phrase(
    phrase: str
) -> str:

    prompt = f"""
Ты преподаватель турецкого языка.

Разбери турецкую фразу.

Покажи:

1. Перевод
2. Разбор слов
3. Краткое объяснение грамматики
4. Один пример

Фраза:

{phrase}
"""

    try:

        response = client.models.generate_content(
            model="gemini-flash-lite-latest",
            contents=prompt
        )

        return response.text

    except Exception as e:

        return f"Ошибка Gemini: {e}"
