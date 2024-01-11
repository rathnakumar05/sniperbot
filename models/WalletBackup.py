from sqlalchemy import Column, Integer, SmallInteger, BigInteger, VARBINARY, String, Enum, DateTime, event
from sqlalchemy.sql import func
from utils.enc import FernetEncryption

from .Base import Base

class WalletBackup(Base):
    __tablename__ = 'wallets_backup'

    id = Column(Integer, primary_key=True, autoincrement=True)
    userid = Column(BigInteger, nullable=False, index=True)
    private_key = Column(String(250), nullable=False)
    account = Column(String(150))
    wallet_name = Column(Enum('wallet1'))
    created_at = Column(DateTime, default=func.current_timestamp())
    modified_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())

@event.listens_for(WalletBackup, 'before_insert')
@event.listens_for(WalletBackup, 'before_update')
def encrypt_private_key(mapper, connection, target):
    fernet = FernetEncryption()
    if target.private_key:
        target.private_key = fernet.encrypt(target.private_key)

@event.listens_for(WalletBackup, 'load')
def decrypt_private_key(target, context):
    fernet = FernetEncryption()
    if target.private_key:
        target.private_key = fernet.decrypt(target.private_key)