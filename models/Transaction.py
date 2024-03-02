from sqlalchemy import Column, Integer, BigInteger, String, DateTime, SmallInteger
from sqlalchemy.sql import func

from .Base import Base

class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    userid = Column(BigInteger, nullable=False)
    tx_hash = Column(String(250), nullable=False)
    tx_method = Column(String(75))
    account = Column(String(150))
    from_addr = Column(String(150))
    from_name = Column(String(200))
    from_symbol = Column(String(150))
    from_decimal = Column(String(45))
    from_value = Column(String(200))
    to_addr = Column(String(150))
    to_name = Column(String(200))
    to_symbol = Column(String(150))
    to_decimal = Column(String(45))
    to_value = Column(String(200))
    fee = Column(String(100))
    version = Column(String(50))
    action = Column(String(45))
    tx_status = Column(SmallInteger)
    created_at = Column(DateTime, default=func.current_timestamp())
    modified_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())