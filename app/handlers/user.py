from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

import app.keyboards.UserKb as kbus
from app.database.requests import (get_user, set_user, update_user, del_user, 
        get_service, get_date, get_free_time, set_reserve, 
        get_reserve, del_reserve, get_media)
import app.keyboards.UserConf as US
from app.state import RegUser, UpdateUser, ReserveService

router_user = Router()

#region MainMenu
async def MainMenu(message: Message, tg_id):
    user = await get_user(tg_id)
    if user:
        await message.answer_photo(await get_media("main"), f"Привет, {user}!\nХочешь маникюрчик?\nТогда скорее записывайся"
                                   , reply_markup=kbus.keyboard(US.main_menu, 2))
    else:
        await message.answer("Регистрируемся?", reply_markup=kbus.keyboard(US.answer("reg_1", "reg_0"), 2))



@router_user.callback_query(F.data.startswith('mainmenu1'))
async def call_main(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    await state.clear()
    await MainMenu(callback.message, callback.from_user.id)
#endregion


#region CommandStart
@router_user.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await message.delete()
    await state.clear()
    await MainMenu(message, message.from_user.id)
#endregion


#region Register
@router_user.callback_query(F.data.startswith('reg_'))
async def register(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    await state.clear()
    check = callback.data.split('_')[1]
    if check == '1':
        await state.set_state(RegUser.name)
        await callback.message.answer("Введите ваше имя ну с фамилией хз:")

    else:
        await callback.message.answer("ту-ту-ту")
        await callback.message.answer("Может все таки?", reply_markup=kbus.keyboard(US.answer("reg_1", "reg_0"), 2))


@router_user.message(RegUser.name)
async def finish_register(message: Message, state: FSMContext):
    if await set_user(message.from_user.id, message.from_user.username, message.text):
        await message.answer("Регистрация прошла успешна!", reply_markup=kbus.keyboard({"Отлично!": "mainmenu1"}, 1))
    else:
        await message.answer("Упс, что то не так!", reply_markup=kbus.keyboard({"Попробовать еще раз": "mainmenu1"}, 1))
    await state.clear()
#endregion


#region UpdateUser
@router_user.callback_query(F.data.startswith("settings"))
async def setting(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    await state.clear()
    user = await get_user(callback.from_user.id)
    if user:
        await callback.message.answer("Выбери что хочешь изменить", reply_markup=kbus.keyboard(US.settings, 1))
    else:
        await callback.message.answer("Похоже, вы еще не зарегистрированы /n Регистрируемся?", 
                                      reply_markup=kbus.keyboard(US.answer("reg_1", "reg_0"), 2))


@router_user.callback_query(F.data.startswith("change_"))
async def change_user(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    change = callback.data.split('_')[1]
    if change == "name":
        await state.set_state(UpdateUser.name)
        await callback.message.answer("Введите ваше имя ну с фамилией хз:")
    elif change == "0":
        await MainMenu(callback.message, callback.from_user.id)
    elif change == "del":
        await callback.message.answer("Вы уверены?", reply_markup=kbus.keyboard(US.answer("del_1", "settings"), 2))


@router_user.message(UpdateUser.name)
async def update_name(message: Message, state: FSMContext):
    name = message.text
    if await update_user(message.from_user.id, name):
        await message.answer(f"Имя успешно изменилось\nВаше новое имя: {name}", reply_markup=kbus.keyboard({"Отлично!": "mainmenu1"}, 1))
    else:
        await message.answer("Упс, что то пошло не так", reply_markup=kbus.keyboard(US.settings, 1))

@router_user.callback_query(F.data.startswith("del_"))
async def delete_user(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    await state.clear()
    if await del_user(callback.from_user.id):
        await callback.message.answer("Ваш аккаунт успешно удален!", reply_markup=kbus.keyboard({"Ок": "mainmenu1"}, 1))
#endregion


#region ReserveService
@router_user.callback_query(F.data.startswith('zap'))
async def choice_service(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    await state.set_state(ReserveService.service)
    text = await get_service()
    if text:
        text["Отмена"] = "mainmenu1"
        await callback.message.answer_photo(await get_media("price"), "Выбирай что будем делать:"
                                            , reply_markup=kbus.keyboard(text, 2))
    else:
        await callback.message.answer("Извини, но сейчас рабочих дней нет(", reply_markup=kbus.keyboard({"Ок": "mainmenu1"}, 1))
    
@router_user.callback_query(StateFilter(ReserveService.service))
async def choice_date(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ReserveService.day)
    await callback.message.delete()
    await callback.answer()
    await state.update_data(name_service=callback.data.split('_')[3])
    await state.update_data(service=callback.data.split('_')[1])
    await state.update_data(time_work=callback.data.split('_')[2]) 
    text = await get_date(int(callback.data.split('_')[2]))
    text["Назад"] = "zap"
    text["Отмена"] = "mainmenu1"
    await callback.message.answer("Доступные записи:", reply_markup=kbus.keyboard(text, 2))


@router_user.callback_query(F.data.startswith('back12'))
async def choice_date(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ReserveService.day)
    await callback.message.delete()
    await callback.answer()
    data = await state.get_data()
    text = await get_date(int(data["time_work"]))
    text["Назад"] = "zap"
    text["Отмена"] = "mainmenu1"
    await callback.message.answer("Доступные записи:", reply_markup=kbus.keyboard(text, 2))


@router_user.callback_query(ReserveService.day)
async def choice_time(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ReserveService.time_start)
    await callback.message.delete()
    await callback.answer()
    await state.update_data(day=callback.data.split('_')[1])
    data = await  state.get_data()
    text = await get_free_time(callback.data.split('_')[1], int(data["time_work"]))
    text["Отмена"] = "mainmenu1"
    text["Назад"] = "back12"
    await callback.message.answer("Доступное время:", reply_markup=kbus.keyboard(text, 2))


@router_user.callback_query(ReserveService.time_start)
async def apply_reserve(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    await state.update_data(day_id=callback.data.split('_')[2])
    await state.update_data(time_start=callback.data.split('_')[1])
    await state.set_state(ReserveService.day_id)
    data = await state.get_data()
    await callback.message.answer(f"Подтверждаете запись?\n" 
                                f"{data['name_service']} на {data['day']} в {data['time_start']}:00", 
                                reply_markup=kbus.keyboard(US.answer("done_1", "done_0"), 2))
    

@router_user.callback_query(ReserveService.day_id)
async def done_reserve(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    answer = callback.data.split('_')[1]
    if answer == '1':
        data = await state.get_data()
        reserve = await set_reserve(callback.from_user.id, data["service"], data["day_id"], data['time_start'], data['time_work'])
        if reserve:
            await state.clear()
            await callback.bot.send_message(chat_id=780621902, text=f" Пользователь {await get_user(callback.from_user.id)}\n"
                                            f"{data['name_service']} на {data['day']} в {data['time_start']}:00")
            await callback.message.answer("Твоя запись сохранилась", reply_markup=kbus.keyboard({"Отлично!": "mainmenu1"}, 1))
        else:
            await state.clear()
            await callback.message.answer("Что-то случило попробуй заново!", reply_markup=kbus.keyboard({"Ок": "mainmenu1"}, 1))
#endregion


#region DelReserve
@router_user.callback_query(F.data.startswith("antizap"))
async def choice_del_res(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer()
    text = await get_reserve(callback.from_user.id)
    if text:
        text["Отмена"] = "mainmenu1"
        await callback.message.answer("Выберите запись, которую хотите отменить:", reply_markup=kbus.keyboard(text, 1))
    else:
        await callback.message.answer("Записей не найдено", reply_markup=kbus.keyboard({"Понятно": "mainmenu1"}, 1))

@router_user.callback_query(F.data.startswith("dateId_"))
async def apply_del_reserve(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    reserve_id = callback.data.split("_")[1]
    if await del_reserve(reserve_id):
        await callback.message.answer("Ваша запись удалена", reply_markup=kbus.keyboard({"Понятно": "mainmenu1"}, 1))
    else:
        await callback.message.answer("Упс что-то не так!", reply_markup=kbus.keyboard({"Жаль": "mainmenu1"}, 1))
#endregion


#region ReturnReserve
@router_user.callback_query(F.data.startswith("myzap"))
async def return_reserve(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer()
    text = await get_reserve(callback.from_user.id)
    if text:
        await callback.message.answer(f"{US.answer_text(text)}", reply_markup=kbus.keyboard({"Ок": "mainmenu1"}, 1))
    else:
        await callback.message.answer("Вы еще не записаны", reply_markup=kbus.keyboard({"Ок": "mainmenu1"}, 1))
#endregion


#region PriceList
@router_user.callback_query(F.data.startswith("price_list"))
async def return_priceList(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer()
    await callback.message.answer_photo(await get_media("price"), reply_markup=kbus.keyboard({"Ок": "mainmenu1"}, 1))
#endregion

# @router_user.message(F.sticker)
# async def update_sticker(message: Message):
#     file_id = message.sticker.file_id
#     await message.answer(file_id)