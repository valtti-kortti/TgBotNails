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
        result = await session.execute(user)
        if result.rowcount > 0:
            await session.commit()
            reserve = delete(Reserve).where(Reserve.user_id == tg_id)
            result = await session.execute(reserve)
            if result.rowcount > 0:
                await session.commit()
            return True
        else:
            await session.rollback()
            return False
    except:
        await session.rollback()
        return False
    

@connection
async def get_users_id(session):
    answer = []
    users = await session.scalars(select(User))
    for user in users:
        answer.append(user.tg_id)
    return answer
#endregion


#region Service
@connection
async def get_service(session):
    services = await session.scalars(select(Service))
    text = {service.name_service: f"ser_{service.id}_{service.time_service}_{service.name_service}" for service in services}
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
async def update_service(session, ser_id, name, time, price):
    try:
        service = update(Service).where(Service.id == ser_id).values(name_service=name, time_service= time, price= price)
        result = await session.execute(service)
        if result.rowcount > 0:
            await session.commit()
            return True
        else:
            await session.rollback()
            return False
    except Exception as e:
        print(e)
        await session.rollback()
        return False
    
@connection
async def set_service(session, name, time, price):
    try:
        service = Service(name_service=name, time_service= time, price= price)
        session.add(service)
        await session.commit()
        return True
    except Exception as e:
        print(e)
        return False
    
@connection
async def del_service(session, id_service):
    try:
        service = delete(Service).where(Service.id == id_service)
        result = await session.execute(service)
        if result.rowcount > 0:
            await session.commit()
            reserve = delete(Reserve).where(Reserve.service_id == id_service)
            result = await session.execute(reserve)
            if result.rowcount > 0:
                await session.commit()
            return True
        else:
            await session.rollback()
            return False
    except Exception as e:
        await session.rollback()
        print(e)
        return False

#endregion


#region Reserve
@connection
async def set_reserve(session, user_id, service_id, time_work_id, time_start, time):
    try:
        reserve = Reserve(user_id= user_id, 
                        service_id=service_id, 
                        time_work_id=time_work_id,
                        time_start=time_start,
                        time=time,
                        )
        session.add(reserve)
        await session.commit()
        return True
    except Exception as e:
        print(e)
        return False
    
@connection
async def get_reserve(session, user_id):
    print("get_reserve")
    text = {}
    if user_id == "admin":
        reserves = await session.scalars(select(Reserve))
        for reserve in reserves:
            day = await session.scalar(select(DateWork).where(DateWork.id == reserve.time_work_id))
            user = await session.scalar(select(User.name).where(User.tg_id == reserve.user_id))
            service = await session.scalar(select(Service.name_service).where(Service.id == reserve.service_id))
            text[f"{user} - {service}: {day.date} {reserve.time_start}:00"] = f"dateId_{reserve.id}_{reserve.user_id}_{service}_{day.date}_{reserve.time_start}:00"

    else:
        reserves = await session.scalars(select(Reserve).where(Reserve.user_id == user_id))
        for reserve in reserves:
            day = await session.scalar(select(DateWork).where(DateWork.id == reserve.time_work_id))
            service = await session.scalar(select(Service.name_service).where(Service.id == reserve.service_id))
            text[f"{service}: {day.date} {reserve.time_start}:00"] = f"dateId_{reserve.id}"
    return text

@connection
async def del_reserve(session, reserve_id):
    try:
        reserve = delete(Reserve).where(Reserve.id == reserve_id)
        result = await session.execute(reserve)
        if result.rowcount > 0:
            await session.commit()
            return True
        else:
            await session.rollback()
            return False
    except Exception as e:
        print(e)
        await session.rollback()
        return False
    
#endregion

#region Media
@connection
async def get_media(session, appointment):
    result = await session.scalar(select(Media.url).where(Media.appointment == appointment))
    if result:
        return result
    else:
        return False
    
@connection
async def update_media(session, appointment, url):
    try:
        user = update(Media).where(Media.appointment == appointment).values(url=url)
        result = await session.execute(user)
        if result.rowcount > 0:
            await session.commit()
            return True
        else:
            await session.rollback()
            return False
    except Exception as e:
        print(e)
        await session.rollback()
        return False
    
#endregion