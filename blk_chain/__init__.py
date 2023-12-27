from blk_chain.ETHChain import EthChain, AsyncEthChain

def connection(chain="ETH"):
    if chain.upper()=="ETH":
        return EthChain()
    return None
    
def async_connection(chain="ETH"):
    if chain.upper()=="ETH":
        return AsyncEthChain()
    return None
