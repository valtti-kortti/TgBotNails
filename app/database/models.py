from sqlalchemy import String, Integer, BigInteger, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession
from dotenv import load_dotenv
import os

load_dotenv()
BaseData = os.getenv("BaseData")
print(BaseData)
engine = create_async_engine(url=BaseData)
async_session = async_sessionmaker(engine, class_=AsyncSession)

class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(BigInteger)
    username: Mapped[str] = mapped_column(String(32), nullable=True)
    name: Mapped[str] = mapped_column(String(20), nullable=True)


class Service(Base):
    __tablename__ = 'services'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name_service: Mapped[str] = mapped_column(String(11))
    time_service: Mapped[int] = mapped_column(Integer)
    price: Mapped[int] = mapped_column(Integer)


class DateWork(Base):
    __tablename__ = 'dateworks'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    date: Mapped[str] = mapped_column(String(15))
    start: Mapped[int] = mapped_column(Integer)
    end: Mapped[int] = mapped_column(Integer)


class Reserve(Base):
    __tablename__ = 'reserves'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    service_id: Mapped[int] = mapped_column(Integer, ForeignKey('services.id'))
    time_work_id: Mapped[int] = mapped_column(Integer)
    time_start: Mapped[int] = mapped_column(Integer, nullable=True)
    time: Mapped[int] = mapped_column(Integer, nullable=True)


class Media(Base):
    __tablename__ = 'media'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    appointment: Mapped[str] = mapped_column(String(10))
    url: Mapped[str] = mapped_column(Text)


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
