from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

import app.keyboards.UserKb as kbus
from app.database.requests import get_user, set_user, update_user, del_user
from config import main_photo, reg_sticker
import app.keyboards.UserConf as US
from app.state import RegUser, UpdateUser, ReserveService

router_user = Router()

#region MainMenu
async def MainMenu(message: Message, tg_id):
    user = await get_user(tg_id)
    await message.answer_photo(main_photo, f"Привет, {user}", reply_markup=kbus.keyboard(US.main_menu, 2))
#endregion


#region CommandStart
@router_user.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await message.delete()
    await state.clear()
    user = await get_user(message.from_user.id)
    if user:
        await MainMenu(message, message.from_user.id)
    else:
        await message.answer_sticker(reg_sticker)
        await message.answer("Регистрируемся?", reply_markup=kbus.keyboard(US.answer("reg1", "reg_0"), 2))
#endregion


#region Register
@router_user.callback_query(F.data.startswith('reg_'))
async def register(callback: CallbackQuery, state: FSMContext):
    check = callback.data.split('_')[1]
    await callback.message.delete()
    if check == '1':
        await state.set_state(RegUser.name)
        await callback.message.answer("Введите ваше имя ну с фамилией хз:")

    else:
        await callback.message.answer("ту-ту-ту")
        await callback.message.answer("Может все таки?", reply_markup=kbus.keyboard(US.answer("reg1", "reg_0"), 2))


@router_user.message(RegUser.name)
async def finish_register(message: Message, state: FSMContext):
    if await set_user(message.from_user.id, message.from_user.username, message.text):
        await message.answer("Все отлично!")
        await MainMenu(message, message.from_user.id)
    else:
        await message.answer("Упс, что то не так!")
    await state.clear()
#endregion


#region UpdateUser
@router_user.callback_query(F.data.startswith("settings"))
async def setting(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer()
    user = await get_user(callback.from_user.id)
    if user:
        await callback.message.answer("Выбери что хочешь изменить", reply_markup=kbus.keyboard(US.settings, 1))
    else:
        await callback.message.answer("Похоже, вы еще не зарегистрированы /n Регистрируемся?", 
                                      reply_markup=kbus.keyboard(US.answer("reg1", "reg_0"), 2))


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
        await callback.message.answer("Вы уверены?", reply_markup=kbus.keyboard(US.answer("del_1", "del_0"), 2))


@router_user.message(UpdateUser.name)
async def update_name(message: Message, state: FSMContext):
    name = message.text
    if await update_user(message.from_user.id, name):
        await message.answer("Имя изменилось")
        await MainMenu(message, message.from_user.id)
    else:
        await message.answer("Упс, что то пошло не так", reply_markup=kbus.keyboard(US.settings, 1))
    await state.clear()

@router_user.callback_query(F.data.startswith("del_"))
async def delete_user(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    check = callback.data.split('_')[1]
    if check == '1':
        if await del_user(callback.from_user.id):
            await callback.message.answer("Регистрируемся?", reply_markup=kbus.keyboard(US.answer("reg1", "reg_0"), 2))

    else:
        await callback.message.answer("Настройки", reply_markup=kbus.keyboard(US.settings, 1))


#endregion


#region ReservService
@router_user.callback_query(F.data.startswith('zap'))
async def choice_service(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.answer()
    await state.set_state(ReserveService.service)
    


#endregion
# @router_user.message(F.sticker)
# async def update_sticker(message: Message):
#     file_id = message.sticker.file_id
#     await message.answer(file_id)