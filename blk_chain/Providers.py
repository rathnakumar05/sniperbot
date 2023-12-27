from web3 import Web3, AsyncWeb3

class Provider:

    url = None

    def __init__(self, url: str) -> None:
        self.url = url

    def get_provider(self) -> Web3:
        return Web3(Web3.HTTPProvider(self.url))
    

class AsyncProvider:
     
    url = None

    def __init__(self, url: str) -> None:
        self.url = url

    def get_provider(self) -> AsyncWeb3:
        return AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(self.url))
    


