from sqlalchemy import create_engine, Column, Integer, BigInteger, String, DateTime, SmallInteger
from sqlalchemy.sql import func

from .Base import Base

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    userid = Column(BigInteger, nullable=False, unique=True)
    username = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))
    is_bot = Column(SmallInteger)
    created_at = Column(DateTime, default=func.current_timestamp())
    modified_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
