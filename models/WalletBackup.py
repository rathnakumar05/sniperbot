from sqlalchemy import Column, Integer, SmallInteger, BigInteger, VARBINARY, String, Enum, DateTime
from sqlalchemy.sql import func

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
