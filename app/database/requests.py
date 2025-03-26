from sqlalchemy import update, select, delete

from .models import User, DateWork, Service, Reserve, Media
from .models import async_session


def connection(func):
    async def wrapper(*args, **kwargs):
        async with async_session() as session:
            return await func(session, *args, **kwargs)
    return wrapper


@connection
async def get_user(session, tg_id):
    user = await session.scalar(select(User).where(User.tg_id == tg_id))
    if user:
        return user.name
    return False

@connection
async def set_user(session, tg_id, username, name):
    try:
        user = User(tg_id=tg_id, username=username, name=name)
        session.add(user)
        await session.commit()
        return True
    except:
        return False
    