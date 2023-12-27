import re
from decimal import Decimal

from blk_chain.TokenAbi import TokenAbi
from models.TblException import TblException
from utils.db import get_sessionmaker

def get_account_addr(w3, private_key):
    if private_key.startswith("0x"):
        private_key = private_key[2:]
    if not re.fullmatch(r'[0-9a-fA-F]{64}', private_key):
        raise Exception("Invalid private key format")
    
    account = w3.eth.account.from_key(private_key)
    sample_msg = b"Hello, world!"
    sample_msg = w3.keccak(sample_msg)
    signature = w3.eth.account.signHash(sample_msg, private_key)
    account_address = account.address

    return account_address

async def is_valid_token(w3, token_addr):
    if not w3.is_address(token_addr):
        return False
    
    if await w3.eth.get_code(w3.to_checksum_address(token_addr)) == b'':
        return False
    
    token_abi = TokenAbi(w3, w3.to_checksum_address(token_addr))

    try:
        token_decimal = await token_abi.async_decimal()
        token_supply = await token_abi.async_supply()
        return True
    except Exception as err:
        return False
    
def is_valid_value(value):
    try:
        value_decimal = Decimal(value)
        if value_decimal <= 0:
            return False
        return True
    except Exception as err:
        return False
    
async def tbl_log(userid, exception = None, exception_type = None, exception_msg = None, reply_to_message = None, callback_data = None, message = None):
    sessionmaker = get_sessionmaker()
    try:
        async with sessionmaker() as session:
            exec_stmt = TblException(
                userid=userid,
                exception=exception,
                exception_type=exception_type,
                exception_msg=exception_msg,
                reply_to_message=reply_to_message,
                callback_data=callback_data,
                message=message
            )
            session.add(exec_stmt)
            await session.commit()
    except Exception as err:
        print("tbl_log exception\n", err)
    return