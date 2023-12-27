import traceback
from typing import Any
from aiogram import Router, types, F
from aiogram.filters.exception import ExceptionTypeFilter
from sqlalchemy.exc import SQLAlchemyError

from handlers.utils.general import tbl_log

error_cb_router = Router(name=__name__)

@error_cb_router.error(ExceptionTypeFilter(SQLAlchemyError), F.update.callback_query.as_("callback_query"))
async def handle_exception(event: types.ErrorEvent, callback_query: types.CallbackQuery):
    userid = callback_query.from_user.id
    await tbl_log(
            userid=userid,
            exception='SQLAlchemyError',
            exception_type=type(event.exception).__name__,
            exception_msg=event.exception,
            callback_data=callback_query.data
    )
    print(traceback.format_exc())
    await callback_query.message.answer("😕 Something went wrong, please try again later! 🔄🙏")
    await callback_query.answer()

@error_cb_router.error(ExceptionTypeFilter(Exception), F.update.callback_query.as_("callback_query"))
async def handle_exception1(event: types.ErrorEvent, callback_query: types.CallbackQuery):
    userid = callback_query.from_user.id
    await tbl_log(
            userid=userid,
            exception='Exception',
            exception_type=type(event.exception).__name__,
            exception_msg=event.exception,
            callback_data=callback_query.data
    )
    print(traceback.format_exc())
    await callback_query.message.answer("😕 Something went wrong, please try again later! 🔄🙏")
    await callback_query.answer()