import asyncio
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
import os

from app.handlers.admin import router_admin
from app.handlers.user import router_user
from app.database.models import async_main


load_dotenv()

BotToken = os.getenv("BotToken")
print(BotToken)

bot = Bot(BotToken)
dp = Dispatcher()

dp.include_router(router_admin)
dp.include_router(router_user)

async def main():
    await async_main()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass