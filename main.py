import os
import sys
import asyncio
import logging
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode

from utils.db import get_sessionmaker
from middlewares.DbSessionMiddleware import DbSessionMiddleware
from handlers.messages import basic_msg_router
from handlers.messages import wallet_msg_router
from handlers.messages import snipe_msg_router
from handlers.messages import error_msg_router
from handlers.callbacks import wallet_cb_router
from handlers.callbacks import snipe_cb_router
from handlers.callbacks import error_cb_router
from utils.general import support_notifier


async def main() -> None:
    try:
        bot = Bot(os.getenv('BOT_TOKEN'), parse_mode=ParseMode.HTML)
        dp = Dispatcher()
        sessionmaker = get_sessionmaker()

        dp.update.middleware(DbSessionMiddleware(sessionmaker=sessionmaker))

        dp.include_router(basic_msg_router)
        dp.include_router(wallet_msg_router)
        dp.include_router(snipe_msg_router)
        dp.include_router(error_msg_router)

        dp.include_router(wallet_cb_router)
        dp.include_router(snipe_cb_router)
        dp.include_router(error_cb_router)

        await bot.set_my_commands([
            types.BotCommand(command="start", description="Start using the bot"),
            types.BotCommand(command="snipe", description="Snipe buy or sell"),
            types.BotCommand(command="wallet", description="Check wallet details"),
            types.BotCommand(command="balance", description="Check Balance details"),
        ])
        await dp.start_polling(bot)
    except Exception as err:
        await support_notifier(
            message_details={
                "status": "ERROR 🛑",
                "message": f"Bot has been crashed, Please check it \nException: {err}"
            }
        )


if __name__ == "__main__":
    load_dotenv()
    # logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    logging.basicConfig(filename="sniperbot.log",
                filemode='a',
                format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
                level=logging.INFO)
    asyncio.run(main())
