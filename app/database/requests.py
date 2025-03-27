from sqlalchemy import update, select, delete

from .models import User, DateWork, Service, Reserve, Media
from .models import async_session


def connection(func):
    async def wrapper(*args, **kwargs):
        async with async_session() as session:
            return await func(session, *args, **kwargs)
    return wrapper


#region User
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
        await session.add(user)
        await session.commit()
        return True
    except:
        return False
    
@connection
async def update_user(session, tg_id, name):
    try:
        user = update(User).where(User.tg_id == tg_id).values(name=name)
        if user:
            await session.execute(user)
            await session.commit()
            return True
        else:
            return False
    except:
        return False
    
@connection
async def del_user(session, tg_id):
    try:
        user = delete(User).where(User.tg_id == tg_id)
        if user:
            await session.execute(user)
            await session.commit()
            return True
        else:
            return False
    except:
        return False
#endregion


#region Service
@connection
async def get_service(session):
    services = await session.scalars(select(Service))
    text = {service.name: service.id for service in services}
    return text

#endregion