from aiogram.fsm.state import StatesGroup, State


class RegUser(StatesGroup):
    name = State()

class UpdateUser(StatesGroup):
    name = State()
    delete = State()

class ReserveService(StatesGroup):
    service = State()
    day = State()
    time_start = State()
    time_work = State()
    day_id = State()
    name_service = State()

class DeleteAdminReserve(StatesGroup):
    reserve_id = State()
    apply = State()

class ReserveServiceAdmin(StatesGroup):
    service = State()
    day = State()
    time_start = State()
    time_work = State()
    day_id = State()
    name_service = State()

class Newsletter(StatesGroup):
    text = State()
    photo = State()
    photo_2 = State()
    text_2 = State()

class NewMedia(StatesGroup):
    main = State()
    price = State()

class ChangeService(StatesGroup):
    name = State()
    time = State()
    price = State()
    id_ser = State()

class NewService(StatesGroup):
    name = State()
    time = State()
    price = State()
    id_ser = State()

class DeleteService(StatesGroup):
    id_service = State()
    rec = State()

class RemindReserve(StatesGroup):
    id_user = State()
    message = State()
    service = State()
    date = State()
    time = State()

class AddWorkDay(StatesGroup):
    day = State()
    start = State()
    end = State()

class CreateNewUser(StatesGroup):
    name = State()