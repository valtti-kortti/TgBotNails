from aiogram import Router, Bot, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

import app.keyboards.UserKb as kbus
from app.database.requests import get_user, set_user
from config import main_photo, reg_sticker
from app.state import RegUser

router_user = Router()

#region CommandStart
@router_user.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await message.delete()
    await state.clear()
    user = await get_user(message.from_user.id)
    if user:
        await message.answer_photo(main_photo, f"Привет, {user}", reply_markup=kbus.main_menu())
    else:
        await message.answer_sticker(reg_sticker)
        await message.answer("Регистрируемся?", reply_markup=kbus.register())
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
        await callback.message.answer("Регистрируемся?", reply_markup=kbus.register())

@router_user.message(RegUser.name)
async def finish_register(message: Message, state: FSMContext):
    if await set_user(message.from_user.id, message.from_user.username, message.text):
        await message.answer("Все отлично!")
        await message.answer_photo(main_photo, f"Привет, {message.text}", reply_markup=kbus.main_menu())
    else:
        await message.answer("Упс, что то не так!")
    

#endregion

# @router_user.message(F.sticker)
# async def update_sticker(message: Message):
#     file_id = message.sticker.file_id
#     await message.answer(file_id)