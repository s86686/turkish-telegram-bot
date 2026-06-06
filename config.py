import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

WEBHOOK_SECRET = os.getenv(
    "WEBHOOK_SECRET",
    "turkish-secret"
)

RENDER_EXTERNAL_URL = os.getenv(
    "RENDER_EXTERNAL_URL"
)

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)
