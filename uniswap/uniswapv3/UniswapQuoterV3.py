import os
import json
from web3 import Web3, AsyncWeb3

class UniswapQuoterV3:

    abi = None
    address = None
    contract = None
    w3 = None

    def __init__(self, w3: AsyncWeb3 | Web3, address: str) -> None:
        self.w3 = w3
        dir_path = os.path.dirname(os.path.realpath(__file__))
        abi_path = os.path.join(dir_path, 'abis', 'uniswap_v3_quoter2_abi.json')
        with open(abi_path, 'r') as file:
            self.abi =  json.load(file)
        self.address = address
        self.contract = w3.eth.contract(address=self.address, abi=self.abi)

    def get_amounts_out(self, amount: int, path: bytes) -> list:
        amount_out, sqrtPriceX96After, initializedTicksCrossed, gasEstimate = self.contract.functions.quoteExactInput(path, amount).call()
        return [amount_out, sqrtPriceX96After, initializedTicksCrossed, gasEstimate]
    
    async def async_get_amounts_out(self, amount: int, path: list) -> list:
        amount_out, sqrtPriceX96After, initializedTicksCrossed, gasEstimate = await self.contract.functions.quoteExactInput(path, amount).call()
        return [amount_out, sqrtPriceX96After, initializedTicksCrossed, gasEstimate]
