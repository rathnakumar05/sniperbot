import json
import os
from web3 import Web3, AsyncWeb3

class TokenAbi:
    abi = None
    address = None
    contract = None
    w3 = None

    def __init__(self, w3: AsyncWeb3 | Web3, address: str) -> None:
        self.w3 = w3
        dir_path = os.path.dirname(os.path.realpath(__file__))
        abi_path = os.path.join(dir_path, 'abis', 'token_abi.json')
        with open(abi_path, 'r') as file:
            self.abi =  json.load(file)
        self.address = address
        self.contract = w3.eth.contract(address=self.address, abi=self.abi)

    def name(self) -> str:
        name = self.contract.functions.name().call()

        return name
    
    async def async_name(self) -> str:
        name = await self.contract.functions.name().call()

        return name
    
    def symbol(self) -> str:
        name = self.contract.functions.symbol().call()

        return name
    
    async def async_symbol(self) -> str:
        symbol = await self.contract.functions.symbol().call()

        return symbol

    def decimal(self) -> int:
        decimal = self.contract.functions.decimals().call()

        return decimal
    
    async def async_decimal(self) -> int:
        decimal = await self.contract.functions.decimals().call()

        return decimal
    
    def supply(self) -> int:
        supply = self.contract.functions.totalSupply().call()

        return supply
    
    async def async_supply(self) -> int:
        supply = await self.contract.functions.totalSupply().call()

        return supply
    
    def balance_of(self, account_address: str) -> int:
        balance = self.contract.functions.balanceOf(account_address).call()

        return balance
    
    async def async_balance_of(self, account_address: str) -> int:
        balance = await self.contract.functions.balanceOf(account_address).call()
        
        return balance
    
    def approve(self, address: str, amount: int, tx_param: dict, private_key: str):
        tx = self.contract.functions.approve(
            address, 
            amount
        ).build_transaction(tx_param)

        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        return tx_hash
    
    async def async_approve(self, address: str, amount: int, tx_param: dict, private_key: str):
        tx = await self.contract.functions.approve(
            address, 
            amount
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