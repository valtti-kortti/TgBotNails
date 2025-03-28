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
        print(tg_id, username, name)
        user = User(tg_id=tg_id, username=username, name=name)
        session.add(user)
        await session.commit()
        return True
    except Exception as e:
        print(e)
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
    text = {service.name_service: f"ser_{service.id}_{service.time_service}" for service in services}
    return text

@connection
async def get_date(session, time):
    text = {}
    dates = await session.scalars(select(DateWork))
    for date in dates:
        reserves = await session.scalars(select(Reserve).where(Reserve.time_work_id == date.id))
        reserve_list = [[reserve.time_start, reserve.time_start + reserve.time] for reserve in reserves]
        reserve_list.sort(key=lambda x: x[0])
        if reserve_list:
            if reserve_list[0][0] - date.start >= time or date.end - reserve_list[-1][1]>= time:
                text[date.date] = f"date_{date.date}"
            else:
                for i in range(1, len(reserve_list)):
                    if reserve_list[i][0] - reserve_list[i - 1][1] >= time:
                        text[date.date] = f"date_{date.date}"
                        break
        else:
            if date.end - date.start >= time:
                text[date.date] = f"date_{date.date}"
    return text

@connection
async def get_free_time(session, day, time_service):
    text = {}
    dates = await session.scalars(select(DateWork).where(DateWork.date == day))
    for date in dates:
        reserves = await session.scalars(select(Reserve).where(Reserve.time_work_id == date.id))
        reserve_list = [[reserve.time_start, reserve.time_start + reserve.time] for reserve in reserves]
        reserve_list.sort(key=lambda x: x[0])
        if reserve_list:
            print("delta = ", reserve_list[0][0] - date.start, "time_ser =", time_service)
            if reserve_list[0][0] - date.start >= time_service:
                for time in range(date.start, reserve_list[0][0] - time_service + 1):
                    text[f"{time}:00"] = f"time_{time}_{date.id}"

            for i in range(1, len(reserve_list)):
                    if reserve_list[i][0] - reserve_list[i - 1][1] >= time_service:
                        for time in range(reserve_list[i - 1][1], reserve_list[i][0] - time_service + 1):
                            text[f"{time}:00"] = f"time_{time}_{date.id}"

            if date.end - reserve_list[-1][1] >= time_service:
                for time in range(reserve_list[-1][1], date.end - time_service + 1):
                    text[f"{time}:00"] = f"time_{time}_{date.id}"
                
        else:
            for time in range(date.start, date.end - time_service + 1):
                text[f"{time}:00"] = f"time_{time}_{date.id}"
    return text

@connection
async def set_reserve(session, user_id, service_id, time_work_id, time_start, time):
    try:
        reserve = Reserve(user_id= user_id, 
                        service_id=service_id, 
                        time_work_id=time_work_id,
                        time_start=time_start,
                        time=time,
                        reserve=True
                        )
        session.add(reserve)
        await session.commit()
        return True
    except Exception as e:
        print(e)
        return False
    

#endregion