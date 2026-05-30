import asyncio
import os

from aiohttp import web

from aiogram import Bot
from aiogram import Dispatcher
from aiogram.types import Update

from config import (
    BOT_TOKEN,
    WEBHOOK_SECRET,
    RENDER_EXTERNAL_URL
)

from db.seed import create_tables

from handlers.start import (
    router as start_router
)

from handlers.lesson import (
    router as lesson_router
)

from handlers.stats import (
    router as stats_router
)

from handlers.settings import (
    router as settings_router
)


bot = Bot(BOT_TOKEN)

dp = Dispatcher()

dp.include_router(start_router)
dp.include_router(lesson_router)
dp.include_router(stats_router)
dp.include_router(settings_router)


WEBHOOK_PATH = f"/webhook/{WEBHOOK_SECRET}"


async def handle_webhook(request):

    data = await request.json()

    update = Update.model_validate(data)

    await dp.feed_update(
        bot=bot,
        update=update
    )

    return web.Response(text="ok")


async def on_startup():

    # create_tables()

    webhook_url = (
        f"{RENDER_EXTERNAL_URL}"
        f"{WEBHOOK_PATH}"
    )

    await bot.set_webhook(
        webhook_url
    )

    print(
        f"Webhook set: {webhook_url}"
    )


async def on_shutdown():

    await bot.delete_webhook()

    await bot.session.close()


async def main():

    await on_startup()

    app = web.Application()

    app.router.add_post(
        WEBHOOK_PATH,
        handle_webhook
    )

    runner = web.AppRunner(app)

    await runner.setup()

    site = web.TCPSite(
        runner,
        host="0.0.0.0",
        port=int(os.getenv("PORT", "10000"))
    )

    await site.start()

    print(
        "Webhook server started"
    )

    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())
