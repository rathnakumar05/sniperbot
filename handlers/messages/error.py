import traceback
from typing import Any
from aiogram import Router, types, F
from aiogram.filters.exception import ExceptionTypeFilter
from sqlalchemy.exc import SQLAlchemyError

from handlers.utils.general import tbl_log
from utils.general import support_notifier

error_msg_router = Router(name=__name__)

@error_msg_router.error(ExceptionTypeFilter(SQLAlchemyError), F.update.message.as_("message"))
async def handle_exception(event: types.ErrorEvent, message: types.Message):
    await message.answer("😕 Something went wrong, please try again later! 🔄🙏")
    
    userid = message.from_user.id
    reply_to_message = None
    if message.reply_to_message:
        reply_to_message = message.reply_to_message.text
    await tbl_log(
            userid = userid,
            exception ='SQLAlchemyError',
            exception_type = type(event.exception).__name__,
            exception_msg = event.exception,
            reply_to_message = reply_to_message,
            callback_data = None,
            message = message.text
    )
    # print(traceback.format_exc())
    await support_notifier(
        message_details={
            "status": "ERROR 🛑",
            "from_user": message.from_user,
            "message": event.exception
        }
    )

@error_msg_router.error(ExceptionTypeFilter(Exception), F.update.message.as_("message"))
async def handle_exception1(event: types.ErrorEvent, message: types.Message):
    await message.answer("😕 Something went wrong, please try again later! 🔄🙏")

    userid = message.from_user.id
    reply_to_message = None
    if message.reply_to_message:
        reply_to_message = message.reply_to_message.text
    await tbl_log(
            userid = userid,
            exception = 'Exception',
            exception_type = type(event.exception).__name__,
            exception_msg = event.exception,
            reply_to_message = reply_to_message,
            callback_data = None,
            message = message.text
    )
    # print(traceback.format_exc())
    await support_notifier(
        message_details={
            "status": "ERROR 🛑",
            "from_user": message.from_user,
            "message": event.exception
        }
    )
