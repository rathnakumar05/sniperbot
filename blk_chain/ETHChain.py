from typing import Any
from web3 import Web3, AsyncWeb3
import os

from blk_chain.Providers import Provider, AsyncProvider

class EthChain(Provider):
    w3 = None
    eth_addr = None
    uniswap_v2_router_addr = None
    uniswap_v2_factory_addr = None

    def __init__(self) -> None:
        url = os.getenv("ETH_PROVIDER")
        super().__init__(url)
        self.w3 = self.get_provider()
        self.eth_addr = os.getenv("ETH_ADDR")
        self.uniswap_v2_router_addr = os.getenv("ETH_UNISWAP_V2_ROUTER_ADDR")
        self.uniswap_v2_factory_addr = os.getenv("ETH_UNISWAP_V2_FACTORY_ADDR")
    
    def __call__(self) -> Any:
        return self.w3

class AsyncEthChain(AsyncProvider):
    w3 = None
    eth_addr = None
    uniswap_v2_router_addr = None
    uniswap_v2_factory_addr = None

    def __init__(self) -> None:
        url = os.getenv("ETH_PROVIDER")
        super().__init__(url)
        self.w3 = self.get_provider()
        self.eth_addr = os.getenv("ETH_ADDR")
        self.uniswap_v2_router_addr = os.getenv("ETH_UNISWAP_V2_ROUTER_ADDR")
        self.uniswap_v2_factory_addr = os.getenv("ETH_UNISWAP_V2_FACTORY_ADDR")
    
    def __call__(self) -> Any:
        return self.w3
