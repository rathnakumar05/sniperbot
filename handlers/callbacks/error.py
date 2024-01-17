import traceback
from typing import Any
from aiogram import Router, types, F
from aiogram.filters.exception import ExceptionTypeFilter
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy.exc import SQLAlchemyError

from handlers.utils.general import tbl_log
from utils.general import support_notifier

error_cb_router = Router(name=__name__)

@error_cb_router.error(ExceptionTypeFilter(TelegramBadRequest), F.update.callback_query.as_("callback_query"))
async def handle_exception(event: types.ErrorEvent, callback_query: types.CallbackQuery):
    await callback_query.answer()
    userid = callback_query.from_user.id
    await tbl_log(
            userid=userid,
            exception='TelegramBadRequest',
            exception_type=type(event.exception).__name__,
            exception_msg=event.exception,
            callback_data=callback_query.data
    )

@error_cb_router.error(ExceptionTypeFilter(SQLAlchemyError), F.update.callback_query.as_("callback_query"))
async def handle_exception(event: types.ErrorEvent, callback_query: types.CallbackQuery):
    await callback_query.message.answer("😕 Something went wrong, please try again later! 🔄🙏")
    userid = callback_query.from_user.id
    await tbl_log(
            userid=userid,
            exception='SQLAlchemyError',
            exception_type=type(event.exception).__name__,
            exception_msg=event.exception,
            callback_data=callback_query.data
    )
#     print(traceback.format_exc())
    await support_notifier(
        message_details={
            "status": "ERROR 🛑",
            "from_user": callback_query.from_user,
            "message": event.exception
        }
    )

@error_cb_router.error(ExceptionTypeFilter(Exception), F.update.callback_query.as_("callback_query"))
async def handle_exception1(event: types.ErrorEvent, callback_query: types.CallbackQuery):
    await callback_query.message.answer("😕 Something went wrong, please try again later! 🔄🙏")
    userid = callback_query.from_user.id
    await tbl_log(
            userid=userid,
            exception='Exception',
            exception_type=type(event.exception).__name__,
            exception_msg=event.exception,
            callback_data=callback_query.data
    )
#     print(traceback.format_exc())
    await support_notifier(
        message_details={
            "status": "ERROR 🛑",
            "from_user": callback_query.from_user,
            "message": event.exception
        }
    )
