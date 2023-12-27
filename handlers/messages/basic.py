from typing import Any
from aiogram import Router, types
from aiogram.filters import CommandStart, Command
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from models.User import User
from models.Wallet import Wallet
from blk_chain.ETHChain import AsyncEthChain
from handlers.callback_factory.WalletCallbackFactory import WalletCallbackFactory
from handlers.callback_factory.SnipeCallbackFactory import SnipeCallbackFactory
from handlers.callback_factory.TokenCallbackFactory import TokenCallbackFactory
from handlers.keyboards.general import start_0, start_1, wallet_0, wallet_1
from utils.keyboards import get_buttons

basic_msg_router = Router(name=__name__)

@basic_msg_router.message(CommandStart())
async def start_command(message: types.Message, sessionmaker: async_sessionmaker) -> Any:
    userid = message.from_user.id
    async with sessionmaker() as session:
        wallet_stmt = select(Wallet).filter_by(userid=userid, wallet_name='wallet1').limit(1)
        wallet = await session.execute(wallet_stmt)
        wallet = wallet.scalars().first()

        if not wallet:
            reply_markup = start_0()
        else:
            reply_markup = start_1()
            
        await message.answer('Hello buddy!')
        await message.answer("📜 Menu 👇", reply_markup=reply_markup)
    return

@basic_msg_router.message(Command("snipe"))
async def snipe_command(message: types.Message, sessionmaker: async_sessionmaker) -> Any:
    keyboard_struct = {
        'buttons': [
            { 'text': 'Buy ⬆️🟢', 'callback_data': SnipeCallbackFactory(action="buy", chain="ETH").pack() },
            { 'text': 'Sell ⬇️🔴', 'callback_data': SnipeCallbackFactory(action="sell", chain="ETH").pack() }
        ],
        'adjust': [2]
    }
    reply_markup = get_buttons(**keyboard_struct)
    await message.answer('⛓️ ETH chain', reply_markup=reply_markup)
    
    return

@basic_msg_router.message(Command('wallet'))
async def wallet_command(message: types.Message, sessionmaker: async_sessionmaker) -> Any:
    userid = message.from_user.id
    async with sessionmaker() as session:
        wallet_stmt = select(Wallet).filter_by(userid=userid, wallet_name='wallet1').limit(1)
        wallet = await session.execute(wallet_stmt)
        wallet = wallet.scalars().first()

        if not wallet:
            reply_markup = wallet_0()
        else:
            reply_markup = wallet_1()
            
        await message.answer("💳 Wallet Menu 👇", reply_markup=reply_markup)
    return

@basic_msg_router.message(Command('balance'))
async def balance_command(message: types.Message, sessionmaker: async_sessionmaker) -> Any:
    userid = message.from_user.id

    error_flag = None

    async with sessionmaker() as session:
        wallet_stmt = select(Wallet).filter_by(userid=userid).limit(1)
        wallet = await session.execute(wallet_stmt)
        wallet = wallet.scalars().first()

        if not wallet:
            error_flag = "no-wallet"
        else:

            connection = AsyncEthChain()
            w3 = connection()

            keyboard_struct = {
                'buttons': [
                    { 'text': 'Ether Balance', 'callback_data': TokenCallbackFactory(action="balance", chain="ETH", token_addr=f"{connection.eth_addr}", value="eth").pack() },
                    { 'text': 'Other Token Balances', 'callback_data': TokenCallbackFactory(action="balance", chain="ETH", token_addr="", value="custom").pack() }

                ],
                'adjust': [2, 1]
            }
            reply_markup = get_buttons(**keyboard_struct)
            await message.answer("💵 Balance Menu 👇", reply_markup=reply_markup)

    if error_flag=="no-wallet":
        await message.answer("🔗 No wallet is currently connected. Please connect your wallet to proceed.")
        await message.edit_text("📜 Menu 👇", reply_markup=start_0())    

    return