import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

from aiogram import Bot, Dispatcher
from handlers.user import user


async def main():
    bot = Bot(token=os.getenv("BOT_API"))
    dp = Dispatcher()
    dp.include_router(user)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        print("It's alive!")
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Ooops!")
