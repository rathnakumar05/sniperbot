import os
import json
from web3 import Web3, AsyncWeb3

class UniswapRouterV3:
    abi = None
    address = None
    contract = None
    w3 = None

    def __init__(self, w3: AsyncWeb3 | Web3, address: str) -> None:
        self.w3 = w3
        dir_path = os.path.dirname(os.path.realpath(__file__))
        abi_path = os.path.join(dir_path, 'abis', 'uniswap_v3_router2_abi.json')
        with open(abi_path, 'r') as file:
            self.abi =  json.load(file)
        self.address = address
        self.contract = w3.eth.contract(address=self.address, abi=self.abi)
    
    def buy(self, path: bytes, tx_param0: tuple, tx_param: dict, private_key: str):
        
        tx = self.contract.functions.exactInput(tx_param0).build_transaction(tx_param)

        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return tx_hash
    
    async def async_buy(self, tx_param0: tuple, tx_param: dict, private_key: str):        
        tx = await self.contract.functions.exactInput(tx_param0).build_transaction(tx_param)

        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=private_key)
        tx_hash = await self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return tx_hash
    
    def sell(self, tx_param0: tuple, tx_param: dict, private_key: str):
        
        tx = self.contract.functions.exactInput(tx_param0).build_transaction(tx_param)

        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        return tx_hash
    
    async def async_sell(self, tx_param0: tuple, tx_param: dict, private_key: str):
        
        tx = await self.contract.functions.exactInput(tx_param0).build_transaction(tx_param)

        signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=private_key)
        tx_hash = await self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

        return tx_hash
    
    def get_receipt(self, tx_hash):
        tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        return tx_receipt
    
    async def async_get_receipt(self, tx_hash):
        tx_receipt = await self.w3.eth.wait_for_transaction_receipt(tx_hash)

        return tx_receipt
