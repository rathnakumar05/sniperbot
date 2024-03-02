import os
import json
from web3 import Web3, AsyncWeb3

class UniswapFactoryV3:

    abi = None
    address = None
    contract = None
    w3 = None

    def __init__(self, w3: AsyncWeb3 | Web3, address: str) -> None:
        self.w3 = w3
        dir_path = os.path.dirname(os.path.realpath(__file__))
        abi_path = os.path.join(dir_path, 'abis', 'uniswap_v3_factory_abi.json')
        with open(abi_path, 'r') as file:
            self.abi =  json.load(file)
        self.address = address
        self.contract = w3.eth.contract(address=self.address, abi=self.abi)

    def get_pair(self, token1: str, token2: str, fee: int) -> str:
        pool_address = self.contract.functions.getPool(token1, token2, fee).call()

        return pool_address

    async def async_get_pair(self, token1: str, token2: str, fee: int) -> str:
        pool_address = await self.contract.functions.getPool(token1, token2, fee).call()
        
        return pool_address
    
    

        