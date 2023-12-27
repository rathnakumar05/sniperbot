import re
from typing import Any
from decimal import Decimal
from aiogram import Router, types
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from blk_chain.ETHChain import AsyncEthChain
from blk_chain.TokenAbi import TokenAbi
from models.User import User
from models.Wallet import Wallet
from handlers.callback_factory.WalletCallbackFactory import WalletCallbackFactory
from handlers.callback_factory.TokenCallbackFactory import TokenCallbackFactory
from handlers.utils.Sniper import Sniper
from handlers.filters.ReplayToMsgFilter import ReplayToMsgFilter
from handlers.filters.ReplayToMsgStartsFilter import ReplayToMsgStartsFilter
from handlers.keyboards.general import start_0, start_1
from handlers.utils.general import is_valid_token, is_valid_value
from utils.keyboards import get_buttons

snipe_msg_router = Router(name=__name__)

@snipe_msg_router.message(ReplayToMsgFilter("please provide the token address to buy"))
async def buy_replay(message: types.Message, sessionmaker: async_sessionmaker) -> Any:
    userid = message.from_user.id
    token_addr = message.text.strip()

    error_flag = None

    async with sessionmaker() as session:
        wallet_stmt = select(Wallet).filter_by(userid=userid, wallet_name='wallet1').limit(1)
        wallet = await session.execute(wallet_stmt)
        wallet = wallet.scalars().first()
        if wallet:
            private_key = wallet.private_key
            connection = AsyncEthChain()
            w3 = connection()

            if await is_valid_token(w3, token_addr):
                account_addr = w3.to_checksum_address(wallet.account)
                eth_addr = w3.to_checksum_address(connection.eth_addr)
                token_addr = w3.to_checksum_address(token_addr)

                eth_balance = await w3.eth.get_balance(account_addr)
                eth_balance = w3.from_wei(eth_balance, 'ether')

                token_abi = TokenAbi(w3, token_addr)
                token_name = await token_abi.async_name()
                token_symbol = await token_abi.async_symbol()

                if eth_balance > 0:
                    keyboard_struct = {
                        'buttons': [
                            { 'text': '1', 'callback_data': TokenCallbackFactory(action="buy", chain="ETH", token_addr=token_addr, value="1").pack() },
                            { 'text': '2', 'callback_data': TokenCallbackFactory(action="buy", chain="ETH", token_addr=token_addr, value="2").pack() },
                            { 'text': '5', 'callback_data': TokenCallbackFactory(action="buy", chain="ETH", token_addr=token_addr, value="5").pack() },
                            { 'text': '0.1', 'callback_data': TokenCallbackFactory(action="buy", chain="ETH", token_addr=token_addr, value="0.1").pack() },
                            { 'text': '0.2', 'callback_data': TokenCallbackFactory(action="buy", chain="ETH", token_addr=token_addr, value="0.2").pack() },
                            { 'text': '0.5', 'callback_data': TokenCallbackFactory(action="buy", chain="ETH", token_addr=token_addr, value="0.5").pack() },
                            { 'text': '0.0001', 'callback_data': TokenCallbackFactory(action="buy", chain="ETH", token_addr=token_addr, value="0.0001").pack() },
                            { 'text': 'Custom', 'callback_data': TokenCallbackFactory(action="buy", chain="ETH", token_addr=token_addr, value="custom").pack() },
                        ],
                        'adjust': [3, 3, 1]
                    }
                    reply_markup = get_buttons(**keyboard_struct)
                    await message.answer(f"Chain: ETH | Token balance: {eth_balance} \nToken name: {token_name} | Token symbol: {token_symbol} \nToken address: {token_addr}", reply_markup=reply_markup)
                else:
                    error_flag = "insufficient"
            else:
                error_flag = "invalid-token"
        else:
            error_flag = "no-wallet"

    if error_flag=="no-wallet":
        await message.answer("🔗 No wallet is currently connected. Please connect your wallet to proceed.")
        await message.answer("📜 Menu 👇", reply_markup=start_0()) 
    elif error_flag=="invalid-token":
        await message.answer("⚠️ Error: Invalid Token Address. Please verify and retry.")
    elif error_flag=="insufficient":
        await message.answer("⚠️ Error: Insufficient balance. Please verify and retry.")
    return

@snipe_msg_router.message(ReplayToMsgStartsFilter("please provide the token value to buy"))
async def token_value_replay(message: types.Message, sessionmaker: async_sessionmaker) -> Any:
    userid = message.from_user.id
    token_value = message.text.strip()

    error_flag = None

    if is_valid_value(token_value):
        token_details = {}

        reply_to_message = message.reply_to_message.text.split('\n')
        for t in reply_to_message[1].split(" | "):
            t = t.split(":")
            token_details[t[0]] = t[1]
        token_details['value'] = token_value
        sniper = Sniper(message=message, sessionmaker=sessionmaker)
        await sniper.buy(**token_details)
    else:
        error_flag = "invalid-value"

    if error_flag=="invalid-value":
        await message.answer("⚠️ Error: InValid amount. Please verify and retry.")
    return
    
@snipe_msg_router.message(ReplayToMsgFilter("please provide the token address to sell"))
async def sell_replay(message: types.Message, sessionmaker: async_sessionmaker) -> Any:
    userid = message.from_user.id
    token_addr = message.text.strip()

    error_flag = None

    async with sessionmaker() as session:
        wallet_stmt = select(Wallet).filter_by(userid=userid, wallet_name='wallet1').limit(1)
        wallet = await session.execute(wallet_stmt)
        wallet = wallet.scalars().first()
        if wallet:
            private_key = wallet.private_key
            connection = AsyncEthChain()
            w3 = connection()

            if await is_valid_token(w3, token_addr):
                account_addr = w3.to_checksum_address(wallet.account)
                eth_addr = w3.to_checksum_address(connection.eth_addr)
                token_addr = w3.to_checksum_address(token_addr)
                if eth_addr!=token_addr:
                    token_abi = TokenAbi(w3, token_addr)
                    token_name = await token_abi.async_name()
                    token_symbol = await token_abi.async_symbol()
                    token_decimal = await token_abi.async_decimal()
                    token_balance = await token_abi.async_balance_of(account_addr)

                    token_balance = token_balance/10**token_decimal

                    if token_balance > 0:
                        keyboard_struct = {
                            'buttons': [
                                { 'text': '1', 'callback_data': TokenCallbackFactory(action="sell", chain="ETH", token_addr=token_addr, value="1").pack() },
                                { 'text': '2', 'callback_data': TokenCallbackFactory(action="sell", chain="ETH", token_addr=token_addr, value="2").pack() },
                                { 'text': '5', 'callback_data': TokenCallbackFactory(action="sell", chain="ETH", token_addr=token_addr, value="5").pack() },
                                { 'text': '0.1', 'callback_data': TokenCallbackFactory(action="sell", chain="ETH", token_addr=token_addr, value="0.1").pack() },
                                { 'text': '0.2', 'callback_data': TokenCallbackFactory(action="sell", chain="ETH", token_addr=token_addr, value="0.2").pack() },
                                { 'text': '0.5', 'callback_data': TokenCallbackFactory(action="sell", chain="ETH", token_addr=token_addr, value="0.5").pack() },
                                { 'text': '25% of total', 'callback_data': TokenCallbackFactory(action="sell", chain="ETH", token_addr=token_addr, value="25%").pack() },
                                { 'text': '50% of total', 'callback_data': TokenCallbackFactory(action="sell", chain="ETH", token_addr=token_addr, value="50%").pack() },
                                { 'text': '75% of total', 'callback_data': TokenCallbackFactory(action="sell", chain="ETH", token_addr=token_addr, value="75%").pack() },
                                { 'text': '90% of total', 'callback_data': TokenCallbackFactory(action="sell", chain="ETH", token_addr=token_addr, value="90%").pack() },
                                { 'text': 'Custom', 'callback_data': TokenCallbackFactory(action="sell", chain="ETH", token_addr=token_addr, value="custom").pack() },
                            ],
                            'adjust': [3, 3, 2, 2, 1]
                        }
                        reply_markup = get_buttons(**keyboard_struct)
                        await message.answer(f"Chain: ETH | Token balance: {token_balance} \nToken name: {token_name} | Token symbol: {token_symbol} \nToken address: {token_addr}", reply_markup=reply_markup)
                    else:
                        error_flag = "insufficient"
                else:
                    error_flag = "invalid-token"
            else:
                error_flag = "invalid-token"
        else:
            error_flag = "no-wallet"

    if error_flag=="no-wallet":
        await message.answer("🔗 No wallet is currently connected. Please connect your wallet to proceed.")
        await message.answer("📜 Menu 👇", reply_markup=start_0()) 
    elif error_flag=="invalid-token":
        await message.answer("⚠️ Error: Invalid Token Address. Please verify and retry.")
    elif error_flag=="insufficient":
        await message.answer("⚠️ Error: Insufficient balance. Please verify and retry.")
    return

@snipe_msg_router.message(ReplayToMsgStartsFilter("please provide the token value to sell"))
async def token_value_replay(message: types.Message, sessionmaker: async_sessionmaker) -> Any:
    userid = message.from_user.id
    token_value = message.text.strip()
    
    error_flag = None

    if is_valid_value(token_value):
        token_details = {}

        reply_to_message = message.reply_to_message.text.split('\n')
        for t in reply_to_message[1].split(" | "):
            t = t.split(":")
            token_details[t[0]] = t[1]
        token_details['value'] = token_value
        sniper = Sniper(message=message, sessionmaker=sessionmaker)
        await sniper.sell(**token_details)
    else:
        error_flag = "invalid-value"

    if error_flag=="invalid-value":
        await message.answer("⚠️ Error: InValid amount. Please verify and retry.")
    return