from aiogram.fsm.state import StatesGroup, State


class RegUser(StatesGroup):
    name = State()

class UpdateUser(StatesGroup):
    name = State()
    delete = State()

class ReserveService(StatesGroup):
    service = State()
    day = State()
    time = State()