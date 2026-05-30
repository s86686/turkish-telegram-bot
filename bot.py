import asyncio

from aiogram import (
    Bot,
    Dispatcher
)

from config import BOT_TOKEN

from handlers.start import (
    router as start_router
)

from handlers.stats import (
    router as stats_router
)

from handlers.settings import (
    router as settings_router
)


async def main():

    bot = Bot(
        token=BOT_TOKEN
    )

    dp = Dispatcher()

    dp.include_router(
        start_router
    )

    dp.include_router(
        stats_router
    )

    dp.include_router(
        settings_router
    )

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
