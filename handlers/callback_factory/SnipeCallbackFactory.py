from aiogram.filters.callback_data import CallbackData


class SnipeCallbackFactory(CallbackData, prefix="snipe"):
    action: str
    chain: str

