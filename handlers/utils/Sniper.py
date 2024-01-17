import os
import requests
from types import SimpleNamespace
from decimal import Decimal
from aiogram import Router, types
from aiogram.enums.parse_mode import ParseMode
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from models.Wallet import Wallet
from models.Transaction import Transaction
from blk_chain.ETHChain import AsyncEthChain
from blk_chain.TokenAbi import TokenAbi
from uniswap.uniswapv2.UniswapFactoryV2 import UniswapFactoryV2
from uniswap.uniswapv2.UniswapRouterV2 import UniswapRouterV2
from handlers.keyboards.general import start_0, start_1

class Sniper():

    message = None
    callback_query = None
    sessionmaker = None

    def __init__(self, message=None, callback_query=None, sessionmaker=None) -> None:
        self.message = message
        self.callback_query = callback_query
        self.sessionmaker = sessionmaker

    def get_web3(self, chain):
        if chain=="ETH":
            return AsyncEthChain()
        
    async def check_liquidity_v2(self, contract_addr, w3, token1, token2):
        uniswap_v2_factory_addr = w3.to_checksum_address(contract_addr)
        uniswap_v2 = UniswapFactoryV2(w3, uniswap_v2_factory_addr)
        pool_addr = await uniswap_v2.async_get_pair(token1=token1, token2=token2)
        return pool_addr
    
    def get_gas_details(self, w3):
        gas_error = False
        gas_tracker_url = os.getenv('GAS_TRACKER_URL')
        gas_tracker = requests.get(gas_tracker_url)

        if(gas_tracker.status_code==200):
            gas_tracker = gas_tracker.json()
            if gas_tracker["status"]=='1':
                gas_price = w3.to_wei(round(float(gas_tracker["result"]["FastGasPrice"])), 'gwei')
                base_price = w3.to_wei(round(float(gas_tracker["result"]["suggestBaseFee"])), 'gwei')
                max_priority_fee_per_gas = abs(gas_price - base_price)
                max_priority_fee_per_gas = 1 if max_priority_fee_per_gas <=0 else max_priority_fee_per_gas
                max_priority_fee_per_gas = int(max_priority_fee_per_gas + (max_priority_fee_per_gas * 0.10))
                max_fee_per_gas = int(gas_price + (gas_price * 0.20))
                gas = 350000
                return [ gas, max_fee_per_gas, max_priority_fee_per_gas ]
            else:
                gas_error = True
        else:
            gas_error = True

        if gas_error:
            raise Exception(gas_tracker)
        return

    async def sell(self, token_addr, value, chain):
        update = self.get_update()
        userid = update.from_user.id
        error_flag = None

        await self.answer(text="Please wait ⏳, this transaction will take 1 to 5 minutes❗ Selling 🛒💸")

        async with self.sessionmaker() as session:
            wallet_stmt = select(Wallet).filter_by(userid=userid, wallet_name='wallet1').limit(1)
            wallet = await session.execute(wallet_stmt)
            wallet = wallet.scalars().first()
            if wallet:
                private_key = wallet.private_key
                connection = self.get_web3(chain)
                w3 = connection()

                account_addr = w3.to_checksum_address(wallet.account)
                eth_addr = w3.to_checksum_address(connection.eth_addr)
                token_addr = w3.to_checksum_address(token_addr)
                path = [token_addr, eth_addr]

                token_abi = TokenAbi(w3, token_addr)
                token_name = await token_abi.async_name()
                token_symbol = await token_abi.async_symbol()
                token_decimal = await token_abi.async_decimal()
                token_balance = await token_abi.async_balance_of(account_addr)

                eth_balance = await w3.eth.get_balance(account_addr)

                if "%" in value:
                    value = value.replace("%", "")
                    value = float(value)/100
                    value = (self.to_fraction(token_balance, token_decimal)*value)

                if(self.to_fraction(token_balance, token_decimal) > Decimal(value)):
                    pool_addr = await self.check_liquidity_v2(contract_addr=connection.uniswap_v2_factory_addr, w3=w3, token1=token_addr, token2=eth_addr)
                    if not pool_addr=="0x0000000000000000000000000000000000000000":
                        gas, max_fee_per_gas, max_priority_fee_per_gas = self.get_gas_details(w3)
                        uniswap_router_v2 = UniswapRouterV2(w3, w3.to_checksum_address(connection.uniswap_v2_router_addr))
                        token_amount, eth_amount = await uniswap_router_v2.async_get_amounts_out(self.from_fraction(Decimal(value), token_decimal), path)
                        # print(w3.from_wei(eth_amount, 'ether'), self.to_fraction(token_amount, token_decimal))
                        amount_out_with_slippage = int(eth_amount * 0.70)
                        latest_block = await w3.eth.get_block('latest')
                        deadline = latest_block['timestamp'] + 10 * 60

                        approve_tx_param = {
                            'gas': gas,
                            'maxFeePerGas': max_fee_per_gas,
                            'maxPriorityFeePerGas': max_priority_fee_per_gas,
                            'nonce': await w3.eth.get_transaction_count(account_addr),
                        }
                        approve_tx = await token_abi.async_approve(
                                address=w3.to_checksum_address(connection.uniswap_v2_router_addr), 
                                amount=(token_amount + 10000), 
                                tx_param=approve_tx_param, 
                                private_key=private_key
                        )

                        try:
                            approve_tx_receipt = await token_abi.async_get_receipt(approve_tx)
                        except Exception as err:
                            approve_tx_receipt = SimpleNamespace( status='na' )
                        
                        transaction_params = {
                            "userid":  userid,
                            "account":  account_addr,
                            "from_addr":  token_addr,
                            "from_name":  token_name,
                            "from_symbol":  token_symbol,
                            "from_decimal":  token_decimal,
                            "from_value":  self.from_fraction(Decimal(value), token_decimal),
                            "to_addr":  eth_addr,
                            "to_name":  "Ether",
                            "to_symbol":  "ETH",
                            "to_decimal":  18,
                            "to_value":  eth_amount,
                            "action": "sell"
                        }
                        transaction_params["tx_method"] = "approve"
                        transaction_params["tx_hash"] = approve_tx.hex()
                        
                        approve_tx_status = 0
                        if approve_tx_receipt.status==1:
                            approve_tx_status = 1
                        elif approve_tx_receipt.status=='na':
                            approve_tx_status = 2
                        transaction_params["tx_status"] = approve_tx_status

                        approve_tx_stmt = Transaction(**transaction_params)
                        try:
                            session.add(approve_tx_stmt)
                            await session.commit()
                        except SQLAlchemyError as err:
                            print(err)
                            pass

                        if approve_tx_receipt.status == 1:
                            tx_param = {
                                'from': account_addr, 
                                'gas': gas,
                                'maxFeePerGas': max_fee_per_gas,
                                'maxPriorityFeePerGas': max_priority_fee_per_gas,
                                'nonce': await w3.eth.get_transaction_count(account_addr),
                            }
                            tx_hash = await uniswap_router_v2.async_sell(
                                    amount=self.from_fraction(Decimal(value), token_decimal), 
                                    min_amount=amount_out_with_slippage, 
                                    path=path, 
                                    account_address=account_addr, 
                                    deadline=deadline,
                                    tx_param=tx_param,
                                    private_key=private_key
                            )

                            try:
                                tx_receipt = await uniswap_router_v2.async_get_receipt(tx_hash)
                            except Exception as err:
                                tx_receipt = SimpleNamespace( status='na' )

                            transaction_params["tx_method"] = "transfer"
                            transaction_params["tx_hash"] = tx_hash.hex()

                            tx_status = 0
                            if tx_receipt.status==1:
                                tx_status = 1
                            elif tx_receipt.status=='na':
                                tx_status = 2
                            transaction_params["tx_status"] = tx_status

                            transaction_stmt = Transaction(**transaction_params)
                            try:
                                session.add(transaction_stmt)
                                await session.commit()
                            except SQLAlchemyError as err:
                                print(err)
                                pass

                            if tx_receipt.status == 1:
                                await self.answer(text=f"🟢 Sold successfully❗ 🟢\n\n📄 Transaction Hash: {tx_hash.hex()} \n💵 Ether Amount: {w3.from_wei(eth_amount, 'ether')} \n<a href=\"{os.getenv("ETH_SCAN_URL")}{tx_hash.hex()}\">check transaction</a>", parse_mode=ParseMode('HTML'))
                            elif tx_receipt.status == 'na':
                                error_flag = "unknown-transaction"
                            else:
                                error_flag = "no-transaction"
                        elif approve_tx_receipt.status == 'na':
                            error_flag = "unknown-approve"      
                        else:
                            error_flag = "no-approve"
                    else:
                        error_flag = "no-liquidity"
                else:
                   error_flag = "insufficient" 

            else:
                error_flag = "no-wallet"

        if error_flag=="no-wallet":
            await self.answer(text="🔗 No wallet is currently connected. Please connect your wallet to proceed.")
            await self.answer(text="📜 Menu 👇", reply_markup=start_0())
        elif error_flag=="insufficient":
            await self.answer(text="⚠️ Error: Insufficient balance. Please verify and retry.") 
        elif error_flag=="no-liquidity":
            await self.answer(text="⚠️ Error: No Liquidity found. Please verify and retry.") 
        elif error_flag=="no-approve":
            await self.answer(text=f"⚠️ Error: Approve transaction failed. Please verify and retry.\n\n📄 Transaction Hash: {approve_tx.hex()} \n<a href=\"{os.getenv("ETH_SCAN_URL")}{approve_tx.hex()}\">check transaction</a>", parse_mode=ParseMode('HTML')) 
        elif error_flag=="unknown-approve":
            await self.answer(text=f"⚠️ Error: Approve transaction failed.")
        elif error_flag=="no-transaction":
            await self.answer(text=f"⚠️ Error: Transaction failed. Please verify and retry.\n\n📄 Transaction Hash: {tx_hash.hex()} \n<a href=\"{os.getenv("ETH_SCAN_URL")}{tx_hash.hex()}\">check transaction</a>", parse_mode=ParseMode('HTML'))
        elif error_flag=="unknown-transaction":
            await self.answer(text=f"⚠️ Error: Transaction failed.")
        elif error_flag:
            await self.answer(text=error_flag)
            
        return 
            
    async def buy(self, token_addr, value, chain):
        update = self.get_update()
        userid = update.from_user.id
        error_flag = None

        await self.answer(text="Please wait ⏳, this transaction will take 1 to 5 minutes❗ Buying 🛒💸")

        async with self.sessionmaker() as session:
            wallet_stmt = select(Wallet).filter_by(userid=userid, wallet_name='wallet1').limit(1)
            wallet = await session.execute(wallet_stmt)
            wallet = wallet.scalars().first()
            if wallet:
                private_key = wallet.private_key
                connection = self.get_web3(chain)
                w3 = connection()

                account_addr = w3.to_checksum_address(wallet.account)
                eth_addr = w3.to_checksum_address(connection.eth_addr)
                token_addr = w3.to_checksum_address(token_addr)
                path = [eth_addr, token_addr]

                token_abi = TokenAbi(w3, token_addr)
                token_name = await token_abi.async_name()
                token_symbol = await token_abi.async_symbol()
                token_decimal = await token_abi.async_decimal()

                eth_balance = await w3.eth.get_balance(account_addr)

                if(w3.from_wei(eth_balance, 'ether') > Decimal(value)):
                    pool_addr = await self.check_liquidity_v2(contract_addr=connection.uniswap_v2_factory_addr, w3=w3, token1=eth_addr, token2=token_addr)
                    if not pool_addr=="0x0000000000000000000000000000000000000000":
                        gas, max_fee_per_gas, max_priority_fee_per_gas = self.get_gas_details(w3)
                        uniswap_router_v2 = UniswapRouterV2(w3, w3.to_checksum_address(connection.uniswap_v2_router_addr))
                        eth_amount, token_amount = await uniswap_router_v2.async_get_amounts_out(w3.to_wei(value, 'ether'), path)
                        # print(w3.from_wei(eth_amount, 'ether'), self.to_fraction(token_amount, token_decimal))
                        amount_out_with_slippage = int(token_amount * 0.70)
                        latest_block = await w3.eth.get_block('latest')
                        deadline = latest_block['timestamp'] + 10 * 60
                        tx_param = {
                            'from': account_addr,
                            'value': w3.to_wei(value, 'ether'),  
                            'gas': gas,
                            'maxFeePerGas': max_fee_per_gas,
                            'maxPriorityFeePerGas': max_priority_fee_per_gas,
                            'nonce': await w3.eth.get_transaction_count(account_addr),
                        }
                        tx_hash = await uniswap_router_v2.async_buy(
                                min_amount = amount_out_with_slippage,
                                path = path,
                                account_address = account_addr,
                                deadline = deadline,
                                private_key = private_key,
                                tx_param = tx_param
                        )
                        try:
                            tx_receipt = await uniswap_router_v2.async_get_receipt(tx_hash)
                        except Exception as err:
                            tx_receipt = SimpleNamespace( status='na' )

                        transaction_params = {
                            "userid":  userid,
                            "tx_hash":  tx_hash.hex(),
                            "tx_method":  "transfer",
                            "account":  account_addr,
                            "from_addr":  eth_addr,
                            "from_name":  "Ether",
                            "from_symbol":  "ETH",
                            "from_decimal":  18,
                            "from_value":  w3.to_wei(value, 'ether'),
                            "to_addr":  token_addr,
                            "to_name":  token_name,
                            "to_symbol":  token_symbol,
                            "to_decimal":  token_decimal,
                            "to_value":  token_amount,
                            "action": "buy"
                        }
                        
                        tx_status = 0
                        if tx_receipt.status==1:
                            tx_status = 1
                        elif tx_receipt.status=='na':
                            tx_status = 2
                        transaction_params["tx_status"] = tx_status

                        transaction_stmt = Transaction(**transaction_params)
                        try:
                            session.add(transaction_stmt)
                            await session.commit()
                        except SQLAlchemyError as err:
                            print(err)
                            pass

                        if tx_receipt.status == 1:
                            await self.answer(text=f"🟢 Bought successfully❗ 🟢\n\n📄 Transaction Hash: {tx_hash.hex()} \n💵 {token_name} Amount: {self.to_fraction(token_amount, token_decimal)} \n<a href=\"{os.getenv("ETH_SCAN_URL")}{tx_hash.hex()}\">check transaction</a>", parse_mode=ParseMode('HTML'))
                        elif tx_receipt.status == 'na':
                            error_flag = "unknown-transaction"
                        else:
                            error_flag = "no-transaction"
                    else:
                        error_flag = "no-liquidity"
                else:
                   error_flag = "insufficient" 

            else:
                error_flag = "no-wallet"

        if error_flag=="no-wallet":
            await self.answer(text="🔗 No wallet is currently connected. Please connect your wallet to proceed.")
            await self.answer(text="📜 Menu 👇", reply_markup=start_0())
        elif error_flag=="insufficient":
            await self.answer(text="⚠️ Error: Insufficient balance. Please verify and retry.") 
        elif error_flag=="no-liquidity":
            await self.answer(text="⚠️ Error: No Liquidity found. Please verify and retry.")  
        elif error_flag=="no-transaction":
            await self.answer(text=f"⚠️ Error: Transaction failed. Please verify and retry.\n\n📄 Transaction Hash: {tx_hash.hex()} \n<a href=\"{os.getenv("ETH_SCAN_URL")}{tx_hash.hex()}\">check transaction</a>", parse_mode=ParseMode('HTML'))
        elif error_flag=="unknown-transaction":
            await self.answer(text=f"⚠️ Error: Transaction failed.")
        elif error_flag:
            await self.answer(text=error_flag)
            
        return 

    def to_fraction(self, value, decimal):
        return value / 10**decimal
    
    def from_fraction(self, value, decimal):
        return int(value * 10**decimal)

    def get_update(self):
        if self.message:
            return self.message
        elif self.callback_query:
            return self.callback_query
        else: 
            raise Exception("update is not found in sniper") 

    def get_message(self):
        if self.message:
            return self.message
        elif self.callback_query:
            return self.callback_query.message
        else: 
            raise Exception("update is not found in sniper") 
           
    async def answer(self, **data):
        update = self.get_message()
        await update.answer(**data)