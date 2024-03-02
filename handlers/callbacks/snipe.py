from typing import Any
from aiogram import Router, types, F
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from blk_chain.ETHChain import AsyncEthChain
from blk_chain.TokenAbi import TokenAbi
from models.User import User
from models.Wallet import Wallet
from handlers.callback_factory.SnipeCallbackFactory import SnipeCallbackFactory
from handlers.callback_factory.TokenCallbackFactory import TokenCallbackFactory
from handlers.keyboards.general import start_0, start_1
from handlers.utils.Sniper import Sniper
from handlers.utils.SniperV3 import SniperV3
from utils.keyboards import get_buttons

snipe_cb_router = Router(name=__name__)

@snipe_cb_router.callback_query(SnipeCallbackFactory.filter(F.action=='start'))
async def start(callback_query: types.CallbackQuery, callback_data: SnipeCallbackFactory, sessionmaker: async_sessionmaker) -> Any:
    keyboard_struct = {
        'buttons': [
            { 'text': 'Buy ⬆️🟢', 'callback_data': SnipeCallbackFactory(action="buy", chain="ETH").pack() },
            { 'text': 'Sell ⬇️🔴', 'callback_data': SnipeCallbackFactory(action="sell", chain="ETH").pack() }
        ],
        'adjust': [2]
    }
    reply_markup = get_buttons(**keyboard_struct)
    await callback_query.message.answer('⛓️ ETH chain', reply_markup=reply_markup)
    
    await callback_query.answer()
    return

@snipe_cb_router.callback_query(SnipeCallbackFactory.filter(F.action=='buy'))
async def buy(callback_query: types.CallbackQuery, callback_data: SnipeCallbackFactory, sessionmaker: async_sessionmaker) -> Any:
    userid = callback_query.from_user.id

    error_flag = None

    async with sessionmaker() as session:
        wallet_stmt = select(Wallet).filter_by(userid=userid, wallet_name='wallet1').limit(1)
        wallet = await session.execute(wallet_stmt)
        wallet = wallet.scalars().first()
        if wallet:
            private_key = wallet.private_key
            connection = AsyncEthChain()
            w3 = connection()

            account_addr = w3.to_checksum_address(wallet.account)
            eth_addr = w3.to_checksum_address(connection.eth_addr)

            eth_balance = await w3.eth.get_balance(account_addr)
            eth_balance = w3.from_wei(eth_balance, 'ether')

            await callback_query.message.answer(f"💵 Current ETH Balance: {eth_balance}")
            await callback_query.message.answer(f"please provide the token address to buy", reply_markup=types.ForceReply())
        else:
            error_flag = "no-wallet"
            
    if error_flag=="no-wallet":
        await callback_query.message.answer("🔗 No wallet is currently connected. Please connect your wallet to proceed.")
        await callback_query.message.edit_text("📜 Menu 👇", reply_markup=start_0()) 

    await callback_query.answer()
    return

@snipe_cb_router.callback_query(TokenCallbackFactory.filter(F.action=='buy'), TokenCallbackFactory.filter(F.value!='custom'))
async def value_buy(callback_query: types.CallbackQuery, callback_data: TokenCallbackFactory, sessionmaker: async_sessionmaker) -> Any:
    token_addr = callback_data.token_addr
    value = callback_data.value
    chain = callback_data.chain
    sniper = Sniper(callback_query=callback_query, sessionmaker=sessionmaker)
    if(await sniper.buy(token_addr=token_addr, value=value, chain=chain)==False):
        sniper = SniperV3(callback_query=callback_query, sessionmaker=sessionmaker)
        await sniper.buy(token_addr=token_addr, value=value, chain=chain)
    
    return

@snipe_cb_router.callback_query(TokenCallbackFactory.filter(F.action=='buy'), TokenCallbackFactory.filter(F.value=='custom'))
async def custom_buy(callback_query: types.CallbackQuery, callback_data: TokenCallbackFactory, sessionmaker: async_sessionmaker) -> Any:
    token_addr = callback_data.token_addr
    chain = callback_data.chain

    connection = AsyncEthChain()
    w3 = connection()

    token_abi = TokenAbi(w3, token_addr)
    token_name = await token_abi.async_name()
    token_symbol = await token_abi.async_symbol()
    await callback_query.message.answer(f"please provide the token value to buy\nchain:{chain} | token_addr:{token_addr}\ntoken_name: {token_name} | token_symbol:{token_symbol}", reply_markup=types.ForceReply())
    
    await callback_query.answer()
    return

@snipe_cb_router.callback_query(SnipeCallbackFactory.filter(F.action=='sell'))
async def sell(callback_query: types.CallbackQuery, callback_data: SnipeCallbackFactory, sessionmaker: async_sessionmaker) -> Any:
    userid = callback_query.from_user.id

    error_flag = None

    async with sessionmaker() as session:
        wallet_stmt = select(Wallet).filter_by(userid=userid, wallet_name='wallet1').limit(1)
        wallet = await session.execute(wallet_stmt)
        wallet = wallet.scalars().first()
        if wallet:
            private_key = wallet.private_key
            connection = AsyncEthChain()
            w3 = connection()

            account_addr = w3.to_checksum_address(wallet.account)
            eth_addr = w3.to_checksum_address(connection.eth_addr)

            eth_balance = await w3.eth.get_balance(account_addr)
            eth_balance = w3.from_wei(eth_balance, 'ether')

            await callback_query.message.answer(f"💵 Current ETH Balance: {eth_balance}")
            await callback_query.message.answer(f"please provide the token address to sell", reply_markup=types.ForceReply())
        else:
            error_flag = "no-wallet"


    if error_flag=="no-wallet":
        await callback_query.message.answer("🔗 No wallet is currently connected. Please connect your wallet to proceed.")
        await callback_query.message.edit_text("📜 Menu 👇", reply_markup=start_0()) 
            
    await callback_query.answer()
    return

@snipe_cb_router.callback_query(TokenCallbackFactory.filter(F.action=='sell'), TokenCallbackFactory.filter(F.value!='custom'))
async def value_sell(callback_query: types.CallbackQuery, callback_data: TokenCallbackFactory, sessionmaker: async_sessionmaker) -> Any:
    token_addr = callback_data.token_addr
    value = callback_data.value
    chain = callback_data.chain
    sniper = Sniper(callback_query=callback_query, sessionmaker=sessionmaker)
    if(await sniper.sell(token_addr=token_addr, value=value, chain=chain)==False):
        sniper = SniperV3(callback_query=callback_query, sessionmaker=sessionmaker)
        await sniper.sell(token_addr=token_addr, value=value, chain=chain)

    return

@snipe_cb_router.callback_query(TokenCallbackFactory.filter(F.action=='sell'), TokenCallbackFactory.filter(F.value=='custom'))
async def custom_sell(callback_query: types.CallbackQuery, callback_data: TokenCallbackFactory, sessionmaker: async_sessionmaker) -> Any:
    token_addr = callback_data.token_addr
    chain = callback_data.chain

    connection = AsyncEthChain()
    w3 = connection()

    token_abi = TokenAbi(w3, token_addr)
    token_name = await token_abi.async_name()
    token_symbol = await token_abi.async_symbol()
    await callback_query.message.answer(f"please provide the token value to sell\nchain:{chain} | token_addr:{token_addr}\ntoken_name: {token_name} | token_symbol:{token_symbol}", reply_markup=types.ForceReply())
    
    await callback_query.answer()
    return
