import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

def get_sessionmaker():
    engine = create_async_engine(
        url=os.getenv('MYSQL_URL'), 
        echo=False,
        pool_pre_ping=True,  
        pool_recycle=1800,  
        pool_size=10,
        max_overflow=20,
    )
    sessionmaker = async_sessionmaker(
        engine, 
        expire_on_commit=False,
        class_=AsyncSession,
    )

    return sessionmaker