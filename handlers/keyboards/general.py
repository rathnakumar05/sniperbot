from handlers.callback_factory.WalletCallbackFactory import WalletCallbackFactory
from handlers.callback_factory.SnipeCallbackFactory import SnipeCallbackFactory
from utils.keyboards import get_buttons

def start_0():
    keyboard_struct = {
        'buttons': [
            { 'text': 'Generate Wallet', 'callback_data': WalletCallbackFactory(action="generate").pack() },
            { 'text': 'Add Wallet', 'callback_data': WalletCallbackFactory(action="add").pack() },
            { 'text': 'Snipe', 'callback_data': SnipeCallbackFactory(action="start", chain="").pack() },
            { 'text': 'Show Balance', 'callback_data': WalletCallbackFactory(action="balance").pack() }
        ],
        'adjust': [2, 1]
    }
    reply_markup = get_buttons(**keyboard_struct)
    return reply_markup

def start_1():
    keyboard_struct = {
        'buttons': [
            { 'text': 'Show Wallet', 'callback_data': WalletCallbackFactory(action="show").pack() },
            { 'text': 'Update Wallet', 'callback_data': WalletCallbackFactory(action="update").pack() },
            { 'text': 'Snipe', 'callback_data': SnipeCallbackFactory(action="start", chain="").pack() },
            { 'text': 'Show Balance', 'callback_data': WalletCallbackFactory(action="balance").pack() }
        ],
        'adjust': [2, 1]
    }
    reply_markup = get_buttons(**keyboard_struct)
    return reply_markup

def wallet_0():
    keyboard_struct = {
        'buttons': [
            { 'text': 'Generate Wallet', 'callback_data': WalletCallbackFactory(action="generate").pack() },
            { 'text': 'Add Wallet', 'callback_data': WalletCallbackFactory(action="add").pack() },
        ],
        'adjust': [2, 1]
    }
    reply_markup = get_buttons(**keyboard_struct)
    return reply_markup

def wallet_1():
    keyboard_struct = {
        'buttons': [
            { 'text': 'Show Wallet', 'callback_data': WalletCallbackFactory(action="show").pack() },
            { 'text': 'Update Wallet', 'callback_data': WalletCallbackFactory(action="update").pack() }
        ],
        'adjust': [2, 1]
    }
    reply_markup = get_buttons(**keyboard_struct)
    return reply_markup