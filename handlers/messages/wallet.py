import re
from typing import Any
from aiogram import Router, types
from aiogram.enums.parse_mode import ParseMode
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from blk_chain.ETHChain import AsyncEthChain
from blk_chain.TokenAbi import TokenAbi
from models.User import User
from models.Wallet import Wallet
from models.WalletBackup import WalletBackup
from handlers.callback_factory.WalletCallbackFactory import WalletCallbackFactory
from handlers.filters.ReplayToMsgFilter import ReplayToMsgFilter
from handlers.filters.ReplayToMsgStartsFilter import ReplayToMsgStartsFilter
from handlers.utils.general import is_valid_token, get_account_addr
from handlers.keyboards.general import start_0, start_1
from utils.keyboards import get_buttons

wallet_msg_router = Router(name=__name__)

@wallet_msg_router.message(ReplayToMsgFilter("please provide the private key"))
async def add_wallet_replay(message: types.Message, sessionmaker: async_sessionmaker) -> Any:
    userid = message.from_user.id
    private_key = message.text.strip()

    error_flag = None

    connection = AsyncEthChain()
    w3 = connection()

    async with sessionmaker() as session:
        wallet_stmt = select(Wallet).filter_by(userid=userid, wallet_name="wallet1").limit(1)
        wallet = await session.execute(wallet_stmt)
        wallet = wallet.scalars().first()
        try:
            if not wallet:
                private_key_flag = 'N'
                try:
                    account_address = get_account_addr(w3, private_key)
                    private_key_flag = 'Y'
                except Exception as err:
                    private_key_flag = 'N'
                    pass
                if private_key_flag=='Y':
                    add_stmt = User(
                        userid = message.from_user.id,
                        username = message.from_user.username,
                        first_name = message.from_user.first_name,
                        last_name = message.from_user.last_name,
                        is_bot = message.from_user.is_bot
                    )
                    session.add(add_stmt)
                    wallet_stmt = Wallet(
                        userid = userid,
                        private_key = private_key,
                        account = account_address,
                        wallet_name = 'wallet1',
                        status = True
                    )
                    session.add(wallet_stmt)
                    wallet_bkup_stmt = WalletBackup(
                        userid = userid,
                        private_key = private_key,
                        account = account_address,
                        wallet_name = 'wallet1'
                    )
                    session.add(wallet_bkup_stmt)
                    await session.commit()
                    await message.answer(
                            f"✅ Wallet details:\n\n"
                    	    f"Address: `{account_address}`\n"
		                    f"Private key: ||{private_key}||\n\n",
		                    parse_mode=ParseMode('MarkdownV2')
                    )
                else:
                    error_flag = "invalid-privatekey"
            else:
                error_flag = "yes-wallet"
        except SQLAlchemyError as err:
            await session.rollback()
            raise err
        
    if error_flag=="yes-wallet":
        await message.answer("🛑 wallet already added")
        await message.answer("📜 Menu 👇", reply_markup=start_1())
    elif error_flag=="invalid-privatekey":
        await message.answer("⚠️ Error: Invalid Private Key. Please verify and retry.")
    
    return

@wallet_msg_router.message(ReplayToMsgFilter("please provide the private key to update"))
async def update_wallet(message: types.Message, sessionmaker: async_sessionmaker) -> Any:
    userid = message.from_user.id
    private_key = message.text.strip()

    error_flag = None

    connection = AsyncEthChain()
    w3 = connection()

    async with sessionmaker() as session:
        wallet_stmt = select(Wallet).filter_by(userid=userid, wallet_name='wallet1').limit(1)
        wallet = await session.execute(wallet_stmt)
        wallet = wallet.scalars().first()
        try:
            if wallet:
                private_key_flag = 'N'
                try:
                    account_address = get_account_addr(w3, private_key)
                    private_key_flag = 'Y'
                except Exception as err:
                    private_key_flag = 'N'
                    pass
                if private_key_flag=='Y':
                    wallet.private_key = private_key
                    wallet.account = account_address
                    wallet_bkup_stmt = WalletBackup(
                        userid = userid,
                        private_key = private_key,
                        account = account_address,
                        wallet_name = 'wallet1'
                    )
                    session.add(wallet_bkup_stmt)
                    await session.commit()
                    await message.answer(
                            f"✅ Wallet details:\n\n"
                    	    f"Address: `{account_address}`\n"
		                    f"Private key: ||{private_key}||\n\n",
		                    parse_mode=ParseMode('MarkdownV2')
                    )
                else:
                    error_flag = "invalid-privatekey"
            else:
                error_flag = 'no-wallet'
        except SQLAlchemyError as err:
            await session.rollback()
            raise err
        
    if error_flag=="yes-wallet":
        await message.answer("🛑 wallet already added")
        await message.answer("📜 Menu 👇", reply_markup=start_1())
    elif error_flag=="invalid-privatekey":
        await message.answer("⚠️ Error: Invalid Private Key. Please verify and retry.")
    elif error_flag=="no-wallet":
        await message.answer("🔗 No wallet is currently connected. Please connect your wallet to proceed.")
        await message.answer("📜 Menu 👇", reply_markup=start_0())
    return

@wallet_msg_router.message(ReplayToMsgStartsFilter("please provide the token address to check balance"))
async def balance_replay(message: types.Message, sessionmaker: async_sessionmaker) -> Any:
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


                token_abi = TokenAbi(w3, token_addr)
                token_name = await token_abi.async_name()
                token_symbol = await token_abi.async_symbol()
                token_decimal = await token_abi.async_decimal()
                token_balance = await token_abi.async_balance_of(account_addr)

                token_balance = token_balance/10**token_decimal

                await message.answer(f"💵 {token_name} Balance ({token_symbol}): {token_balance}")
            else:
                error_flag = "invalid-token"
        else:
            error_flag = "no-wallet"

    if error_flag=="no-wallet":
        await message.answer("🔗 No wallet is currently connected. Please connect your wallet to proceed.")
        await message.answer("📜 Menu 👇", reply_markup=start_0())
    elif error_flag=="invalid-token":
        await message.answer("⚠️ Error: Invalid Token Address. Please verify and retry.")
    return