from aiogram import types
from aiogram.filters import Filter

class ReplayToMsgStartsFilter(Filter):
    def __init__(self, reply_to_message: str) -> None:
        self.reply_to_message = reply_to_message

    async def __call__(self, message: types.Message) -> bool:
        return message.reply_to_message is not None and message.reply_to_message.text.startswith(self.reply_to_message)