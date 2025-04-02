from sqlalchemy import update, select, delete
from .models import User, DateWork, Service, Reserve, Media
from .models import async_session

from logging_config import setup_logger


logger = setup_logger()

def connection(func):
    async def wrapper(*args, **kwargs):
        async with async_session() as session:
            return await func(session, *args, **kwargs)
    return wrapper


#region User
@connection
async def get_user(session, tg_id = None):
    if tg_id:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            return user.name
        return False
    else:
        try:
            users = await session.scalars(select(User))
            text = {}
            for user in users:
                if isinstance(user.tg_id, str):
                    text[user.name] = f"usre_{user.tg_id}"
            return text
        except Exception as e:
            logger.error(f"Oшибка get_user: {e}", exc_info=True)
            return False
        
@connection
async def get_user_for_admin(session):
    try:
        users = await session.scalars(select(User))
        text = {}
        for user in users:
            print(str(user.tg_id))
            if str(user.tg_id).startswith("<"):
                text[user.name] = f"userize_{user.tg_id}"
            print(text)
        return text
    except Exception as e:
        logger.error(f"Oшибка get_user_for_admin: {e}", exc_info=True)
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
        logger.error(f"Oшибка set_user: {e}", exc_info=True)
        return False
    
@connection
async def update_user(session, tg_id, name):
    try:
        user = update(User).where(User.tg_id == tg_id).values(name=name)
        result = await session.execute(user)
        if result.rowcount > 0:
            await session.commit()
            return True
        else:
            await session.rollback()
            return False
    except Exception as e:
        logger.error(f"Oшибка update_user: {e}", exc_info=True)
        await session.rollback()
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
    except Exception as e:
        logger.error(f"Oшибка del_user: {e}", exc_info=True)
        await session.rollback()
        return False
    

@connection
async def get_users_id(session):
    answer = []
    try:
        users = await session.scalars(select(User))
        for user in users:
            if isinstance(user.tg_id, int):
                answer.append(user.tg_id)
        return answer
    except Exception as e:
        logger.error(f"Oшибка get_user_id: {e}", exc_info=True)
        return []
#endregion


#region Service
@connection
async def get_service(session):
    try:
        services = await session.scalars(select(Service))
        text = {service.name_service: f"ser_{service.id}_{service.time_service}_{service.name_service}" for service in services}
        return text
    except Exception as e:
        logger.error(f"Oшибка get_service: {e}", exc_info=True)
        return {}

@connection
async def get_date(session, time):
    text = {}
    try:
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
    except Exception as e:
        logger.error(f"Oшибка get_date: {e}", exc_info=True)
        return {}

@connection
async def get_free_time(session, day, time_service):
    text = {}
    try:
        dates = await session.scalars(select(DateWork).where(DateWork.date == day))
        for date in dates:
            reserves = await session.scalars(select(Reserve).where(Reserve.time_work_id == date.id))
            reserve_list = [[reserve.time_start, reserve.time_start + reserve.time] for reserve in reserves]
            reserve_list.sort(key=lambda x: x[0])
            if reserve_list:
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
    except Exception as e:
        logger.error(f"Oшибка get_free_time: {e}", exc_info=True)
        return {}

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
        logger.error(f"Oшибка update_service: {e}", exc_info=True)
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
        logger.error(f"Oшибка set_service: {e}", exc_info=True)
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
        logger.error(f"Oшибка del_service: {e}", exc_info=True)
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
        logger.error(f"Oшибка set_reserve: {e}", exc_info=True)
        return False
    
@connection
async def get_reserve(session, user_id = None, reserve_id = None):
    text = {}
    try:
        if not user_id and not reserve_id:
            reserves = await session.scalars(select(Reserve))
            for reserve in reserves:
                day = await session.scalar(select(DateWork).where(DateWork.id == reserve.time_work_id))
                user = await session.scalar(select(User.name).where(User.tg_id == reserve.user_id))
                service = await session.scalar(select(Service.name_service).where(Service.id == reserve.service_id))
                text[f"{user} {service}: {day.date} {reserve.time_start}:00"] = f"dateId_{reserve.id}"
        if reserve_id:
            reserve = await session.scalar(select(Reserve).where(Reserve.id == reserve_id))
            day = await session.scalar(select(DateWork).where(DateWork.id == reserve.time_work_id))
            user = await session.scalar(select(User.name).where(User.tg_id == reserve.user_id))
            service = await session.scalar(select(Service.name_service).where(Service.id == reserve.service_id))
            text = {
                    "user_id": reserve.user_id,
                    "service": service,
                    "date": day.date,
                    "time": f"{reserve.time_start}:00",
            }
        else:
            reserves = await session.scalars(select(Reserve).where(Reserve.user_id == user_id))
            for reserve in reserves:
                day = await session.scalar(select(DateWork).where(DateWork.id == reserve.time_work_id))
                service = await session.scalar(select(Service.name_service).where(Service.id == reserve.service_id))
                text[f"{service}: {day.date} {reserve.time_start}:00"] = f"dateId_{reserve.id}"
        return text
    except Exception as e:
        logger.error(f"Oшибка get_reserve: {e}", exc_info=True)
        return {}

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
        logger.error(f"Oшибка del_reserve: {e}", exc_info=True)
        await session.rollback()
        return False
    
#endregion

#region Media
@connection
async def get_media(session, appointment):
    try:
        result = await session.scalar(select(Media.url).where(Media.appointment == appointment))
        if result:
            return result
        else:
            return False
    except Exception as e:
        logger.error(f"Oшибка get_media: {e}", exc_info=True)
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
        logger.error(f"Oшибка update_media: {e}", exc_info=True)
        await session.rollback()
        return False
    
#endregion

#region WorkDay
@connection
async def set_workday(session, date, start, end):
    try:
        workday = DateWork(date= date, start= start, end= end)
        session.add(workday)
        await session.commit()
        return True
    except Exception as e:
        logger.error(f"Oшибка set_workday: {e}", exc_info=True)
        return False
    
@connection 
async def get_workday(session, id_day=None):
    text = {}
    if not id_day:
        try:
            workdays = await session.scalars(select(DateWork))
            for day in workdays:
                key = f"{day.date} {day.start}:00 - {day.end}:00"
                value = f"dateworkid_{day.id}"
                text[key] = value
            return text
        except Exception as e:
            logger.error(f"Oшибка get_workday: {e}", exc_info=True)
            return False
    else:
        try:
            workday = await session.scalar(select(DateWork).where(DateWork.id == id_day))
            text[f"{workday.date}, {workday.start}:00 - {workday.end}:00"] = f"remove_day_id_{id_day}"
            return text
        except Exception as e:
            logger.error(f"Oшибка get_workday: {e}", exc_info=True)
            return {}
    
@connection
async def delete_workday(session, id_day):
    try:
        date = delete(DateWork).where(DateWork.id == id_day)
        result = await session.execute(date)
        if result.rowcount > 0:
            await session.commit()
            reserve = delete(Reserve).where(Reserve.time_work_id == id_day)
            result = await session.execute(reserve)
            if result.rowcount > 0:
                await session.commit()
            return True
        else:
            await session.rollback()
            return False
    except Exception as e:
        logger.error(f"Oшибка delete_workday: {e}", exc_info=True)
        await session.rollback()
        return False





#endregion