import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

def get_sessionmaker():
    engine = create_async_engine(url=os.getenv('MYSQL_URL'), echo=False)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

    return sessionmaker