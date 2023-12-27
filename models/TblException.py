from sqlalchemy import Column, Integer, BigInteger, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

from .Base import Base

class TblException(Base):
    __tablename__ = 'tbl_exceptions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    userid = Column(BigInteger, nullable=False)
    exception = Column(String(150), default=None)
    exception_type = Column(String(150), default=None)
    exception_msg = Column(String(500), default=None)
    reply_to_message = Column(String(350), default=None)
    callback_data = Column(String(350), default=None)
    message = Column(String(350), default=None)
    created_at = Column(DateTime, default=func.current_timestamp())
    modified_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
