from aiogram.fsm.state import State, StatesGroup

class AuthForm(StatesGroup):
    email = State()
    password = State()
    confirm = State()

class RegisterFrom(StatesGroup):
    first_name = State()
    last_name = State()
    email = State()
    phone = State()
    sms_code = State()
    phone_confirm = State()
    agreement = State()
    confirm = State()