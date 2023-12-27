from typing import Any
from aiogram import Router, types, F, enums
from aiogram.enums.parse_mode import ParseMode
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from blk_chain.ETHChain import AsyncEthChain
from blk_chain.TokenAbi import TokenAbi
from models.User import User
from models.Wallet import Wallet
from models.WalletBackup import WalletBackup
from handlers.callback_factory.WalletCallbackFactory import WalletCallbackFactory
from handlers.callback_factory.TokenCallbackFactory import TokenCallbackFactory
from handlers.keyboards.general import start_0, start_1
from utils.keyboards import get_buttons

wallet_cb_router = Router(name=__name__)

@wallet_cb_router.callback_query(WalletCallbackFactory.filter(F.action=='generate'))
async def generate_wallet(callback_query: types.CallbackQuery, callback_data: WalletCallbackFactory, sessionmaker: async_sessionmaker) -> Any:
    userid = callback_query.from_user.id
    connection = AsyncEthChain()
    w3 = connection()

    error_flag = None
    
    account = w3.eth.account.create()
    account_address = account.address
    private_key = account.key.hex()
    async with sessionmaker() as session:
        wallet_stmt = select(Wallet).filter_by(userid=userid, wallet_name='wallet1').limit(1)
        wallet = await session.execute(wallet_stmt)
        wallet = wallet.scalars().first()

        try:
            if not wallet:
                add_stmt = User(
                    userid = callback_query.from_user.id,
                    username = callback_query.from_user.username,
                    first_name = callback_query.from_user.first_name,
                    last_name = callback_query.from_user.last_name,
                    is_bot = callback_query.from_user.is_bot
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
                await callback_query.message.answer(
                        f"✅ Wallet details:\n\n"
                    	f"Address: `{account_address}`\n"
		                f"Private key: ||{private_key}||\n\n",
		                parse_mode=ParseMode('MarkdownV2')
                )
            else:
                error_flag = 'yes-wallet'
                
        except SQLAlchemyError as err:
            await session.rollback()
            raise err
    
    if error_flag=="yes-wallet":
        await callback_query.message.answer("🛑 wallet already added")
        await callback_query.message.edit_text("📜 Menu 👇", reply_markup=start_1())

    await callback_query.answer()
    return

@wallet_cb_router.callback_query(WalletCallbackFactory.filter(F.action=='show'))
async def show_wallet(callback_query: types.CallbackQuery, callback_data: WalletCallbackFactory, sessionmaker: async_sessionmaker) -> Any:
    userid = callback_query.from_user.id

    error_flag = None

    async with sessionmaker() as session:
        wallet_stmt = select(Wallet).filter_by(userid=userid).limit(1)
        wallet = await session.execute(wallet_stmt)
        wallet = wallet.scalars().first()

        if not wallet:
            error_flag = "no-wallet"
        else:
            await callback_query.message.answer(
                    f"✅ Wallet details:\n\n"
                	f"Address: `{wallet.account}`\n"
		            f"Private key: ||{wallet.private_key}||\n\n",
		            parse_mode=ParseMode('MarkdownV2')
            )

    if error_flag=="no-wallet":
        await callback_query.message.answer("🔗 No wallet is currently connected. Please connect your wallet to proceed.")
        await callback_query.message.edit_text("📜 Menu 👇", reply_markup=start_0())

    await callback_query.answer()
    return
    

@wallet_cb_router.callback_query(WalletCallbackFactory.filter(F.action=='add'))
async def add_wallet(callback_query: types.CallbackQuery, callback_data: WalletCallbackFactory, sessionmaker: async_sessionmaker) -> Any:
    userid = callback_query.from_user.id

    error_flag = None

    async with sessionmaker() as session:
        wallet_stmt = select(Wallet).filter_by(userid=userid).limit(1)
        wallet = await session.execute(wallet_stmt)
        wallet = wallet.scalars().first()

        if not wallet:
            await callback_query.message.answer("please provide the private key", reply_markup=types.ForceReply())
        else:
            error_flag = "yes-wallet"

    if error_flag=="yes-wallet":
        await callback_query.message.answer("🛑 wallet already added")
        await callback_query.message.edit_text("📜 Menu 👇", reply_markup=start_1())  

    await callback_query.answer()
    return

@wallet_cb_router.callback_query(WalletCallbackFactory.filter(F.action=='update'))
async def update_wallet(callback_query: types.CallbackQuery, callback_data: WalletCallbackFactory, sessionmaker: async_sessionmaker) -> Any:
    userid = callback_query.from_user.id

    error_flag = None

    async with sessionmaker() as session:
        wallet_stmt = select(Wallet).filter_by(userid=userid).limit(1)
        wallet = await session.execute(wallet_stmt)
        wallet = wallet.scalars().first()

        if not wallet:
            error_flag = "no-wallet"
        else:
            await callback_query.message.answer("please provide the private key to update", reply_markup=types.ForceReply())

    if error_flag=="no-wallet":
        await callback_query.message.answer("🔗 No wallet is currently connected. Please connect your wallet to proceed.")
        await callback_query.message.edit_text("📜 Menu 👇", reply_markup=start_0())   

    await callback_query.answer()
    return

@wallet_cb_router.callback_query(WalletCallbackFactory.filter(F.action=='balance'))
async def show_balance(callback_query: types.CallbackQuery, callback_data: WalletCallbackFactory, sessionmaker: async_sessionmaker) -> Any:
    userid = callback_query.from_user.id

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
            await callback_query.message.answer("💵 Balance Menu 👇", reply_markup=reply_markup)

    if error_flag=="no-wallet":
        await callback_query.message.answer("🔗 No wallet is currently connected. Please connect your wallet to proceed.")
        await callback_query.message.edit_text("📜 Menu 👇", reply_markup=start_0())    

    await callback_query.answer()
    return

@wallet_cb_router.callback_query(TokenCallbackFactory.filter(F.action=='balance'), TokenCallbackFactory.filter(F.value!='custom'))
async def no_custom_balance(callback_query: types.CallbackQuery, callback_data: TokenCallbackFactory, sessionmaker: async_sessionmaker) -> Any:
    userid = callback_query.from_user.id
    token_addr = callback_data.token_addr

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

            account_addr = w3.to_checksum_address(wallet.account)
            token_addr = w3.to_checksum_address(token_addr)
            
            token_balance = await w3.eth.get_balance(account_addr)

            await callback_query.message.answer(f"💵 Ether Balance (ETH): {w3.from_wei(token_balance, 'ether')}")
    
    if error_flag=="no-wallet":
        await callback_query.message.answer("🔗 No wallet is currently connected. Please connect your wallet to proceed.")
        await callback_query.message.edit_text("📜 Menu 👇", reply_markup=start_0())    

    await callback_query.answer()
    return

@wallet_cb_router.callback_query(TokenCallbackFactory.filter(F.action=='balance'), TokenCallbackFactory.filter(F.value=='custom'))
async def custom_balance(callback_query: types.CallbackQuery, callback_data: TokenCallbackFactory, sessionmaker: async_sessionmaker) -> Any:
    userid = callback_query.from_user.id
    chain = callback_data.chain

    error_flag = None

    async with sessionmaker() as session:
        wallet_stmt = select(Wallet).filter_by(userid=userid).limit(1)
        wallet = await session.execute(wallet_stmt)
        wallet = wallet.scalars().first()

        if not wallet:
            error_flag = "no-wallet"
        else:
            await callback_query.message.answer(f"please provide the token address to check balance\nchain:{chain}", reply_markup=types.ForceReply())
    
    if error_flag=="no-wallet":
        await callback_query.message.answer("🔗 No wallet is currently connected. Please connect your wallet to proceed.")
        await callback_query.message.edit_text("📜 Menu 👇", reply_markup=start_0())  

    await callback_query.answer()
    return