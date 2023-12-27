from aiogram.filters.callback_data import CallbackData


class TokenCallbackFactory(CallbackData, prefix="token"):
    action: str
    chain: str
    token_addr: str
    value: str

