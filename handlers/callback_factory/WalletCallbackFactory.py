from aiogram.filters.callback_data import CallbackData


class WalletCallbackFactory(CallbackData, prefix="wallet"):
    action: str

