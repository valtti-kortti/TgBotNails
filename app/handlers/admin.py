from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import random

import app.keyboards.UserKb as kbus
import app.keyboards.AdminConf as AD
from app.database.requests import (get_users_id, get_service, get_date, 
        get_free_time, set_reserve, get_reserve, del_reserve, get_media, 
        update_media, update_service, set_service, del_service, get_user, 
        set_workday, get_workday, delete_workday, set_user, del_user, get_user_for_admin)
from app.state import (DeleteAdminReserve, ReserveServiceAdmin, 
                        Newsletter, NewMedia, ChangeService, NewService, 
                        DeleteService, RemindReserve, AddWorkDay, CreateNewUser)

router_admin = Router()

async def MainMenu(message: Message):
    print("adminmenu")
    await message.answer("Выбери действие:", reply_markup=kbus.keyboard(AD.main_menu, 2))


@router_admin.callback_query(F.data.startswith("adminmenu"))
async def call_main(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    await state.clear()
    await MainMenu(callback.message)


@router_admin.message(Command("admin"))
async def call_admin(message: Message, state: FSMContext):
    await message.delete()
    await state.clear()
    print(message.from_user.id)
    if message.from_user.id in [6812714026, 780621902]:
        await MainMenu(message)

#region View Reserve
@router_admin.callback_query(F.data.startswith("view_rec"))
async def view_record(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    await state.clear()
    text = await get_reserve()
    if text:
        await callback.message.answer(f"{AD.answer_text(text)}", reply_markup=kbus.keyboard({"Ок": "adminmenu"}, 1))
    else:
        await callback.message.answer("Записей не найдено", reply_markup=kbus.keyboard({"Ок": "adminmenu"}, 1))
#endregion


#region Delete Reserve
@router_admin.callback_query(F.data.startswith("delete_rec"))
async def delete_reserve(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    await state.clear()
    text = await get_reserve()
    if text:
        text["Отмена"] = "adminmenu"
        await state.set_state(DeleteAdminReserve.reserve_id)
        await callback.message.answer(f"Выбери запись для удаления: ", reply_markup=kbus.keyboard(text, 1))
    else:
        await callback.message.answer("Записей не найдено", reply_markup=kbus.keyboard({"Ок": "adminmenu"}, 1))

@router_admin.callback_query(DeleteAdminReserve.reserve_id)
async def apply_delete(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    await state.update_data(reserve_id=callback.data.split('_')[1])
    await state.set_state(DeleteAdminReserve.apply)
    await callback.message.answer("Удаляем?", reply_markup=kbus.keyboard(AD.answer("delA_1", "adminmenu"), 2))

@router_admin.callback_query(F.data.startswith("delA_1"))
async def complete_delete(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    data = await state.get_data()
    if await del_reserve(data["reserve_id"]):
        await callback.message.answer("Запись удалена!")
        await state.clear()
        await MainMenu(callback.message)
    else:
        await callback.message.answer("Упс что то не так!")
        await state.clear()
        await MainMenu(callback.message)
#endregion


#region Add Record
@router_admin.callback_query(F.data.startswith("add_rec"))
async def add_record(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    await state.clear()
    await state.set_state(ReserveServiceAdmin.service)
    text = await get_service()
    if text:
        text["Отмена"] = "adminmenu"
        await callback.message.answer_photo(await get_media("price"), "Выбирай услугу:", reply_markup=kbus.keyboard(text, 2))
    else:
        await callback.message.answer("Доступных слотов нет", reply_markup=kbus.keyboard({"Ок": "adminmenu"}, 1))


@router_admin.callback_query(ReserveServiceAdmin.service)
async def choice_date(callback: CallbackQuery, state: FSMContext):
    print("admin")
    await state.set_state(ReserveServiceAdmin.day)
    await callback.message.delete()
    await callback.answer()
    await state.update_data(name_service=callback.data.split('_')[3])
    await state.update_data(service=callback.data.split('_')[1])
    await state.update_data(time_work=callback.data.split('_')[2]) 
    text = await get_date(int(callback.data.split('_')[2]))
    text["Назад"] = "add_rec"
    text["Отмена"] = "adminmenu"
    await callback.message.answer("Доступные записи:", reply_markup=kbus.keyboard(text, 2))


@router_admin.callback_query(F.data.startswith('back_admin'))
async def choice_date(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ReserveServiceAdmin.day)
    await callback.message.delete()
    await callback.answer()
    data = await state.get_data()
    text = await get_date(int(data["time_work"]))
    text["Назад"] = "add_rec"
    text["Отмена"] = "adminmenu"
    await callback.message.answer("Доступные записи:", reply_markup=kbus.keyboard(text, 2))


@router_admin.callback_query(ReserveServiceAdmin.day)
async def choice_time(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ReserveServiceAdmin.time_start)
    await callback.message.delete()
    await callback.answer()
    await state.update_data(day=callback.data.split('_')[1])
    data = await  state.get_data()
    text = await get_free_time(callback.data.split('_')[1], int(data["time_work"]))
    text["Отмена"] = "adminmenu"
    text["Назад"] = "back_admin"
    await callback.message.answer("Доступное время:", reply_markup=kbus.keyboard(text, 2))


@router_admin.callback_query(ReserveServiceAdmin.time_start)
async def apply_reserve(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    await state.update_data(day_id=callback.data.split('_')[2])
    await state.update_data(time_start=callback.data.split('_')[1])
    await state.set_state(ReserveServiceAdmin.day_id)
    data = await state.get_data()
    await callback.message.answer(f"Подтверждаете запись?\n" 
                                f"{data['name_service']} на {data['day']} в {data['time_start']}:00", 
                                reply_markup=kbus.keyboard(AD.answer("doneA_1", "adminmenu"), 2))
    

@router_admin.callback_query(F.data.startswith('doneA_'))
async def done_reserve_id(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    await state.set_state(ReserveServiceAdmin.time_work)
    users = await get_user_for_admin()
    if users:
        users["Отмена"] = "adminmenu"
        await callback.message.answer("Выбери Юзера", reply_markup=kbus.keyboard(users, 2))
    else:
        await callback.message.answer("Юзеров нет", reply_markup=kbus.keyboard({"Отлично": "adminmenu"}, 1))


@router_admin.callback_query(F.data.startswith('userize_'))
async def done_reserve(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    data = await state.get_data()
    reserve = await set_reserve(callback.data.split('_')[1], data["service"], data["day_id"], data['time_start'], data['time_work'])
    if reserve:
        await state.clear()
        await callback.message.answer("Твоя записи сохранилась", reply_markup=kbus.keyboard({"Отлично": "adminmenu"}, 1))
    else:
        await state.clear()
        await callback.message.answer("Что-то случило попробуй заново!", reply_markup=kbus.keyboard({"Плохо": "adminmenu"}, 1))
#endregion

#region Newsletter
@router_admin.callback_query(F.data.startswith("newsletter"))
async def newsletter_choice(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    await state.clear()
    await callback.message.answer(f"Выбери способ отправки", reply_markup=kbus.keyboard({"Текс": "newslet_text", 
                                                                                         "Фото": "newslet_photo", 
                                                                                         "Текст + фото": "newslet_textphoto",
                                                                                         "Отмена": "adminmenu"}, 2))
    
@router_admin.callback_query(F.data.startswith("newslet_"))
async def newsletter(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    await state.clear()
    data = callback.data.split('_')[1]
    if data == "text":
        await state.set_state(Newsletter.text)
        await callback.message.answer("Набери текст:")
    elif data == "photo":
        await state.set_state(Newsletter.photo)
        await callback.message.answer("Отправь фото:")
    else:
        await state.set_state(Newsletter.photo_2)
        await callback.message.answer("Отправь фото:")


@router_admin.message(Newsletter.text)
async def newsletter_text(message: Message, state: FSMContext):
    await message.delete()
    await state.update_data(text= message.text)
    await message.answer(f"Ваш текст\n {message.text}\n ОТПРАВИТЬ?", reply_markup=kbus.keyboard(AD.answer("news_t", "adminmenu"), 2))


@router_admin.message(Newsletter.photo)
async def newsletter_photo(message: Message, state: FSMContext):
    await message.delete()
    await state.update_data(photo= message.photo[-1].file_id)
    await message.answer_photo(message.photo[-1].file_id, reply_markup=kbus.keyboard(AD.answer("news_p", "adminmenu"), 2))

@router_admin.message(Newsletter.photo_2)
async def newsletter_photo_2(message: Message, state: FSMContext):
    await message.delete()
    await state.update_data(photo_2= message.photo[-1].file_id)
    await state.set_state(Newsletter.text_2)
    await message.answer("Набери текст:")

@router_admin.message(Newsletter.text_2)
async def newsletter_text_2(message: Message, state: FSMContext):
    await message.delete()
    await state.update_data(text_2= message.text)
    data = await state.get_data()
    await message.answer_photo(data["photo_2"],f"{message.text}\n ОТПРАВИТЬ?", reply_markup=kbus.keyboard(AD.answer("news_tp", "adminmenu"), 2))


@router_admin.callback_query(F.data.startswith("news_"))
async def send_newsletter(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    answer = callback.data.split('_')[1]
    users = await get_users_id()
    data = await state.get_data()
    if answer == "t":
        for user in users:
            await callback.bot.send_message(chat_id=user, text= data["text"])
    elif answer == "p":
        for user in users:
            await callback.bot.send_photo(chat_id=user, photo= data["photo"])
    else:
        for user in users:
            await callback.bot.send_photo(chat_id=user, photo= data["photo_2"], caption= data["text_2"])
    
    await callback.message.answer("Рассылка успешно отправлена", reply_markup=kbus.keyboard({"Ок": "adminmenu"}, 1))
#endregion

#region Change Media
@router_admin.callback_query(F.data.startswith("update_media"))
async def choice_media(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    await state.clear()
    text = {"Основное": "mainPH", "Прайс": "pricePH", "Отмена": "adminmenu"}
    await callback.message.answer("Какое фото ты хочешь изменить?", reply_markup=kbus.keyboard(text, 2))


@router_admin.callback_query(F.data.startswith("mainPH"))
async def main_ph_change(callback: CallbackQuery):
    photo = await get_media("main")
    await callback.message.answer_photo(photo, "Меняем?", reply_markup=kbus.keyboard(AD.answer("main_change", "adminmenu"), 2))


@router_admin.callback_query(F.data.startswith("main_change"))
async def main_ph_change(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.set_state(NewMedia.main)
    await callback.message.answer("Пришли новое фото:")


@router_admin.message(NewMedia.main)
async def complete_main(message: Message):
    photo = message.photo[-1].file_id
    if await update_media("main", photo):
        await message.answer_photo(photo, "Твое фото заменилось!", reply_markup=kbus.keyboard({"Отлично": "adminmenu"}, 1))
    else:
        await message.answer("Что то случилось!", reply_markup=kbus.keyboard({"Плохо": "adminmenu"}, 1))


@router_admin.callback_query(F.data.startswith("pricePH"))
async def main_ph_change(callback: CallbackQuery):
    photo = await get_media("price")
    await callback.message.answer_photo(photo, "Меняем?", reply_markup=kbus.keyboard(AD.answer("price_change", "adminmenu"), 2))


@router_admin.callback_query(F.data.startswith("price_change"))
async def main_ph_change(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.set_state(NewMedia.price)
    await callback.message.answer("Пришли новое фото:")


@router_admin.message(NewMedia.price)
async def complete_main(message: Message):
    photo = message.photo[-1].file_id
    if await update_media("price", photo):
        await message.answer_photo(photo, "Твое фото заменилось!", reply_markup=kbus.keyboard({"Отлично": "adminmenu"}, 1))
    else:
        await message.answer("Что то случилось!", reply_markup=kbus.keyboard({"Плохо": "adminmenu"}, 1))
#endregion


#region Update Service
@router_admin.callback_query(F.data.startswith("update_service"))
async def change_service(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    await state.clear()
    await state.set_state(ChangeService.id_ser)
    text = await get_service()
    text["Добавить"] = "ser_add"
    text["Отмена"] = "adminmenu"
    await callback.message.answer_photo(await get_media("price"), "Выбери услугу для изменения:", reply_markup=kbus.keyboard(text, 2))


@router_admin.callback_query(ChangeService.id_ser)
async def change_name_service(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    answer = callback.data.split('_')[1]
    if answer != "add":
        await state.update_data(name= callback.data.split('_')[3], time= callback.data.split('_')[2], id_ser=callback.data.split('_')[1])
        await state.set_state(ChangeService.name)
        await callback.message.answer(f"Введи новое название \n Старое название '{callback.data.split('_')[3]}'")
    else:
        await state.set_state(NewService.name)
        await callback.message.answer(f"Введи новое название:")


@router_admin.message(ChangeService.name)
async def change_time_service(message: Message, state: FSMContext):
    await message.delete()
    await state.update_data(name= message.text)
    data = await state.get_data()
    await state.set_state(ChangeService.time)
    await message.answer(f"Введи новое время работы \n Старое время '{data["time"]}'")


@router_admin.message(NewService.name)
async def change_time_service(message: Message, state: FSMContext):
    await message.delete()
    await state.update_data(name= message.text)
    await state.set_state(NewService.time)
    await message.answer(f"Введи новое время работы:")


@router_admin.message(ChangeService.time)
async def change_price_service(message: Message, state: FSMContext):
    await message.delete()
    await state.update_data(time= message.text)
    data = await state.get_data()
    await state.set_state(ChangeService.price)
    await message.answer(f"Введи новую цену \n Старая цена '{data["price"]}'")


@router_admin.message(NewService.time)
async def change_price_service(message: Message, state: FSMContext):
    await message.delete()
    await state.update_data(time= message.text)
    await state.set_state(NewService.price)
    await message.answer(f"Введи новую цену:")


@router_admin.message(ChangeService.price)
async def complete_change_service(message: Message, state: FSMContext):
    await message.delete()
    await state.update_data(price= message.text)
    data = await state.get_data()
    await state.set_state(ChangeService.price)
    await message.answer(f"Новое название {data["name"]}\n Новое время {data["time"]}\n Новая цена {data["price"]}\n Подтверждаем?",
                         reply_markup=kbus.keyboard(AD.answer("change_1", "adminmenu"), 2))
    

@router_admin.message(NewService.price)
async def complete_change_service(message: Message, state: FSMContext):
    await message.delete()
    await state.update_data(price= message.text)
    data = await state.get_data()
    await state.set_state(NewService.price)
    await message.answer(f"Новое название {data["name"]}\n Новое время {data["time"]}\n Новая цена {data["price"]}\n Подтверждаем?",
                         reply_markup=kbus.keyboard(AD.answer("changeser_2", "adminmenu"), 2))
    

@router_admin.callback_query(F.data.startswith("changeser_"))
async def update_service(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    data = await state.get_data()
    if callback.data.split('_')[1] == '1':
        if await update_service(data["id_ser"], data["name"], data["time"], data["price"]):
            await callback.message.answer("Сервис обновился", reply_markup=kbus.keyboard({"Отлично": "adminmenu"}, 1))
        else:
            await callback.message.answer("Что то не так!", reply_markup=kbus.keyboard({"Плохо": "adminmenu"}, 1))
    else:
        if await set_service(data["name"], data["time"], data["price"]):
            await callback.message.answer("Сервис создался", reply_markup=kbus.keyboard({"Отлично": "adminmenu"}, 1))
        else:
            await callback.message.answer("Что то не так!", reply_markup=kbus.keyboard({"Плохо": "adminmenu"}, 1))

#endregion


#region Delete Service
@router_admin.callback_query(F.data.startswith("delete_service"))
async def choice_delete_service(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    await state.clear()
    await state.set_state(DeleteService.id_service)
    text = await get_service()
    text["Отмена"] = "adminmenu"
    await callback.message.answer_photo(await get_media("price"), "Выбери услугу для изменения:", reply_markup=kbus.keyboard(text, 2))


@router_admin.callback_query(DeleteService.id_service)
async def delete_service(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    await state.update_data(id_service=callback.data.split('_')[1])
    await state.set_state(DeleteService.rec)
    await callback.message.answer(f"Удалить {callback.data.split('_')[3]}", reply_markup=kbus.keyboard(AD.answer("deleteser", "adminmenu"), 2))


@router_admin.callback_query(F.data.startswith("deleteser"))
async def complete_delete(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    data = await state.get_data()
    print(data["id_service"])
    try:
        if await del_service(data["id_service"]):
            await callback.message.answer("Услуга удалена!", reply_markup=kbus.keyboard({"Отлично": "adminmenu"}, 1))
        else:
            await callback.message.answer("Что то не так!", reply_markup=kbus.keyboard({"Плохо": "adminmenu"}, 1))
    except Exception as e:
        await callback.message.answer("Что то не так!", reply_markup=kbus.keyboard({"Плохо": "adminmenu"}, 1))
        print(e)
#endregion


#region Send Remind
@router_admin.callback_query(F.data.startswith("remind"))
async def remind_reserve(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    await state.clear()
    text = await get_reserve()
    text["Отмена"] = "adminmenu"
    if text:
        text["Отмена"] = "adminmenu"
        await state.set_state(RemindReserve.id_user)
        await callback.message.answer("Выбери кому ты хочешь отправить напоминание", reply_markup=kbus.keyboard(text, 1))
    else:
        await callback.message.answer("Записей нет", reply_markup=kbus.keyboard({"Плохо": "adminmenu"}, 1))


@router_admin.callback_query(RemindReserve.id_user)
async def remind_message(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    request = await get_reserve(reserve_id=callback.data.split('_')[1])
    await state.update_data(id_user= request["user_id"], 
                            service= request["service"],
                            date= request["date"],
                            time=request["time"],)
    await state.set_state(RemindReserve.message)
    data = await state.get_data()
    user = await get_user(data["id_user"])
    text = f"Привет {user}!\nНапоминаю тебе, о записи на процедуру: {data["service"]}\n{data["date"]} в {data["time"]}"
    await state.update_data(message=text)
    await callback.message.answer(f"Твое сообщение\n{text}\nОтправляем?", reply_markup=kbus.keyboard(AD.answer("rem_message", "adminmenu"), 2))

@router_admin.callback_query(F.data.startswith("rem_message"))
async def remind_message_apply(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    data = await state.get_data()
    await callback.bot.send_message(chat_id=data["id_user"], text=data["message"])
    await callback.message.answer(f"Твое сообщение успешно отправлено!", reply_markup=kbus.keyboard({"Отлично": "adminmenu"}, 1))
#endregion


#region Add Work Day
@router_admin.callback_query(F.data.startswith("add_work_day"))
async def add_work_day(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    await state.clear()
    await state.set_state(AddWorkDay.day)
    await callback.message.answer("Напиши дату\nПример '20 января'")

@router_admin.message(AddWorkDay.day)
async def add_work_day_day(message: Message, state: FSMContext):
    await state.update_data(day=message.text)
    await state.set_state(AddWorkDay.start)
    await message.answer(f"Отлично выбран день {message.text}\nТеперь пиши начало рабочего периода:")

@router_admin.message(AddWorkDay.start)
async def add_work_day_start(message: Message, state: FSMContext):
    await state.update_data(start=message.text)
    await state.set_state(AddWorkDay.end)
    await message.answer(f"Замечательно\nТеперь пиши конц рабочего периода:")

@router_admin.message(AddWorkDay.end)
async def add_work_day_end(message: Message, state: FSMContext):
    await state.update_data(end=message.text)
    data = await state.get_data()
    await message.answer(f"Шоколадно\nСохраняем?\nРабочий день {data["day"]}\nC {data["start"]}:00 до {data["end"]}:00",
                         reply_markup=kbus.keyboard(AD.answer("add_day_new", "adminmenu"), 2))
    
@router_admin.callback_query(F.data.startswith("add_day_new"))
async def new_work_day(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    data = await state.get_data()
    if await set_workday(data["day"], data["start"], data["end"]):
        await callback.message.answer("Новый рабочий день создан", reply_markup=kbus.keyboard({"Отлично": "adminmenu"}, 1))
    else:
        await callback.message.answer("Что то пошло не так", reply_markup=kbus.keyboard({"Плохо": "adminmenu"}, 1))
#endregion

#region Remove DateWork
@router_admin.callback_query(F.data.startswith("remove_work_day"))
async def remove_work_day(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    await state.clear()
    text = await get_workday()
    if text:
        text["Отмена"] = "adminmenu"
        await callback.message.answer("Выбери день:", reply_markup=kbus.keyboard(text, 1))
    else:
        await callback.message.answer("Рабочих дней нет", reply_markup=kbus.keyboard({"Ок": "adminmenu"}, 1))


@router_admin.callback_query(F.data.startswith("dateworkid_"))
async def apply_remove_work_day(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer()
    data = callback.data.split('_')[1]
    text = await get_workday(data)
    if text:
        text["Отмена"] = "adminmenu"
        await callback.message.answer(f"Удаляем?\n{list(text.keys())[0]}", reply_markup=kbus.keyboard(AD.answer(f"{list(text.values())[0]}", "adminmenu"), 2))
    else:
        await callback.message.answer("Ошибка", reply_markup=kbus.keyboard({"Ок": "adminmenu"}, 1))


@router_admin.callback_query(F.data.startswith("remove_day_id_"))
async def remove_work_day_complete(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer()
    data = callback.data.split('_')[3]
    print(data)
    if await delete_workday(data):
        await callback.message.answer("Рабочий день успешно удален", reply_markup=kbus.keyboard({"Зафиксировал": "adminmenu"}, 1))
    else:
        await callback.message.answer("Рабочий день не удален", reply_markup=kbus.keyboard({"Писос": "adminmenu"}, 1))
#endregion

#region View DateWork
@router_admin.callback_query(F.data.startswith("view_date_work"))
async def remove_work_day_complete(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    await state.clear()
    days = await get_workday()
    if days:
        text = "Твои рабочие дни:\n"
        for day in days:
            text += f"{day}\n"
    else:
        text = "Рабочих дней еще нет!"
    await callback.message.answer(text, reply_markup=kbus.keyboard({"Хороши!": "adminmenu"}, 1))
#endregion

#region Create NewUser
@router_admin.callback_query(F.data.startswith("new_user_create"))
async def create_new_user(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    await state.clear()
    await state.set_state(CreateNewUser.name)
    await callback.message.answer("Напиши имя пользователя:")


@router_admin.message(CreateNewUser.name)
async def create_name_user(message: Message, state: FSMContext):
    await message.delete()
    tg_id = random.randint(1000, 1000000)
    tg_id = "<" + str(tg_id)
    if await set_user(tg_id, None, message.text + "(Fake)"):
        await message.answer("Юзер создан", reply_markup=kbus.keyboard({"Хорошо": "adminmenu"}, 1))
    else:
        await message.answer("Что то не так", reply_markup=kbus.keyboard({"Плохо": "adminmenu"}, 1))
#endregion

#region Remove User Fake
@router_admin.callback_query(F.data.startswith("remove_user_create"))
async def remove_new_user(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    await state.clear()
    users = await get_user()
    if users:
        users["Отмена"] = "adminmenu"
        await callback.message.answer("Выбери какого пользователя удалять", reply_markup=kbus.keyboard(users, 1))
    else:
        await callback.message.answer("Юзеры не найдены", reply_markup=kbus.keyboard({"Ок": "adminmenu"}, 1))


@router_admin.callback_query(F.data.startswith("usre_"))
async def remove_new_user_apply(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    await state.clear()
    tg_id = callback.data.split('_')[1]
    if await del_user(tg_id):
        await callback.message.answer("Юзер удален", reply_markup=kbus.keyboard({"Хорошо": "adminmenu"}, 1))
    else:
        await callback.message.answer("Что то не так", reply_markup=kbus.keyboard({"Плохо": "adminmenu"}, 1))






