import os
import json
from web3 import Web3, AsyncWeb3

class UniswapRouterV2:
    abi = None
    address = None
    contract = None
    w3 = None

    def __init__(self, w3: AsyncWeb3 | Web3, address: str) -> None:
        self.w3 = w3
        dir_path = os.path.dirname(os.path.realpath(__file__))
        abi_path = os.path.join(dir_path, 'abis', 'uniswap_v2_router_abi.json')
        with open(abi_path, 'r') as file:
            self.abi =  json.load(file)
        self.address = address
        self.contract = w3.eth.contract(address=self.address, abi=self.abi)

    def get_amounts_out(self, amount: int, path: list) -> list:
        token1_amount, token2_amount = self.contract.functions.getAmountsOut(amount, path).call()

        return [token1_amount, token2_amount]
    
    async def async_get_amounts_out(self, amount: int, path: list) -> list:
        token1_amount, token2_amount = await self.contract.functions.getAmountsOut(amount, path).call()

        return [token1_amount, token2_amount]
    
    def buy(self, min_amount: int, path: list, account_address: str, deadline: str, tx_param: dict, private_key: str):
        tx = self.contract.functions.swapExactETHForTokens(
            min_amount, 
            path,
            account_address,
            deadline
        ).build_transaction(tx_param)

        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        return tx_hash
    
    async def async_buy(self, min_amount: int, path: list, account_address: str, deadline: str, tx_param: dict, private_key: str):
        tx = await self.contract.functions.swapExactETHForTokens(
            min_amount, 
            path,
            account_address,
            deadline
        ).build_transaction(tx_param)
        
        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=private_key)
        tx_hash = await self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        return tx_hash
    
    def sell(self, amount: int, min_amount: int, path: list, account_address: str, deadline: str, tx_param: dict, private_key: str):
        tx = self.contract.functions.swapExactTokensForETH(
            amount,
            min_amount, 
            path,
            account_address,
            deadline
        ).build_transaction(tx_param)

        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        return tx_hash
    
    async def async_sell(self, amount: int, min_amount: int, path: list, account_address: str, deadline: str, tx_param: dict, private_key: str):
        tx = await self.contract.functions.swapExactTokensForETH(
            amount,
            min_amount, 
            path,
            account_address,
            deadline
        ).build_transaction(tx_param)

        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=private_key)
        tx_hash = await self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        return tx_hash
    
    def get_receipt(self, tx_hash):
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        return tx_receipt
    
    async def async_get_receipt(self, tx_hash):
        tx_receipt = await self.w3.eth.wait_for_transaction_receipt(tx_hash)

        return tx_receipt
