from aiogram.fsm.state import StatesGroup, State


class RegUser(StatesGroup):
    name = State()