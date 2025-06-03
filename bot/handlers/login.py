from db.repositories.products_repository import ProductsRepository
from db.repositories.gk_user_repository import GkUserRepository
from db.models.gk_base_info import *
from keyboards.inline import *
from utils.messages.replace import *
from utils.validate.email import is_valid_email
from utils.validate.phone import is_valid_phone
from utils.utils import *
from utils.clients.GK_ApiClient import AsyncAPIClient
from db.sessions import AsyncSessionFactory
from messages.ru_config import RussianMessages
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from states.auth import AuthForm, RegisterFrom
from loguru import logger

async def main_login(call: CallbackQuery, state: FSMContext, data) -> None:
    gk_auth = data.get('gk_auth')
    gk_user = data.get('gk_user')
    db_user = data.get('user')
    try:
        query = call.data.split(':')[1]
    except:
        query = None
    if call.data == 'cancel':
        await state.set_state(None) 
        return await call.message.edit_text(
            RussianMessages().get_start_message(first_name=db_user.first_name),
            reply_markup=get_main_keyboard(gk_auth)
        )
    elif query == 'main':
        if gk_auth:
            try:
                async with AsyncSessionFactory() as session:
                    gk_user_client = GkUserRepository(session)
                    await gk_user_client.delete(gk_user.uuid)
            except Exception as e:
                logger.error('Ошибка выхода из аккаунта GK | {}'.format(e))
                return await call.answer('Ошибка😔 Попробуйте позже', show_alert=True)
            else:
                await call.answer('Вы успешно вышли из аккаунта!', show_alert=True)
                return await call.message.edit_reply_markup(reply_markup=get_main_keyboard(False))
        return await call.message.edit_text(RussianMessages().main_login, reply_markup=get_login_choose())
    elif query == 'auth':
        await call.message.edit_text(RussianMessages().auth_choose_method, reply_markup=get_auth_choose_method())
    elif query == 'auth_email':
        await call.message.edit_text(RussianMessages().auth_email_stage1, reply_markup=get_cancel())
        await state.set_state('auth:email:email')
    elif query == 'auth_phone':
        await call.message.edit_text(RussianMessages().auth_phone_stage1, reply_markup=get_cancel())
        await state.set_state('auth:phone:phone')
    elif query == 'register':
        await call.message.edit_text(RussianMessages().reg_stage1, reply_markup=get_cancel())
        await state.set_state('register:phone')

async def reg_phone_handler(message: Message, state: FSMContext, data) -> None:
    # await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-1)
    phone = message.text
    is_valid, phone = is_valid_phone(phone)
    if not is_valid:
        return await message.answer('Номер введен неверно, попробуйте еще раз\n\n<i>Подсказка: 79998887766</i>', reply_markup=get_back_keyboard())
    async with AsyncAPIClient() as client:
        try:
            send_code = await client.reg_send_code(phone)
        except Exception as e:
            logger.warning(f'Регистрация | Ошибка отправки кода на телефон | {e}')
            return await message.answer('Номер введен неверно, попробуйте еще раз\n\n<i>Подсказка: 79998887766</i>', reply_markup=get_back_keyboard())
    await state.update_data(reg_phone=phone)
    await message.answer(RussianMessages().reg_stage2, reply_markup=get_back_keyboard())
    await state.set_state('register:sms_code')

async def reg_sms_code_handler(message: Message, state: FSMContext, data) -> None:
    # await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-1)
    sms_code = message.text
    state_data = await state.get_data()
    phone = state_data.get('reg_phone')
    if len(sms_code)!= 4:
        return await message.answer('Код введен неверно, попробуйте еще раз\n\n<i>Подсказка: xxxx</i>', reply_markup=get_back_keyboard())
    async with AsyncAPIClient() as client:
        try:
            auth = await client.reg_verify_code(phone=phone, code=sms_code)
        except Exception as e:
            logger.warning(f'Ошибка регистрации | {e}')
            return await message.answer('Неверный код, попробуйте еще раз\n\n<i>Подсказка: xxxx</i>', reply_markup=get_back_keyboard())
    await state.update_data(reg_sms_code=sms_code)
    await message.answer(RussianMessages().reg_stage3, reply_markup=get_back_keyboard())
    await state.set_state('register:name')

async def reg_name_handler(message: Message, state: FSMContext, data) -> None:
    # await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-1)
    name = message.text
    await state.update_data(reg_first_name=name)
    await message.answer(RussianMessages().reg_stage4, reply_markup=get_back_keyboard())
    await state.set_state('register:last_name')

async def reg_last_name_handler(message: Message, state: FSMContext, data) -> None:
    # await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-1)
    last_name = message.text
    await state.update_data(reg_last_name=last_name)
    await message.answer(RussianMessages().reg_stage5, reply_markup=get_back_keyboard())
    await state.set_state('register:email')

async def reg_email_handler(message: Message, state: FSMContext, data) -> None:
    # await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-1)
    email = message.text
    is_valid, email = is_valid_email(email)
    if not is_valid:
        return await message.answer('Email введен неверно, попробуйте еще раз', reply_markup=get_back_keyboard())
    await state.update_data(reg_email=email)
    state_data = await state.get_data()
    await state.set_state(None)
    try:
        result = await reg_new_gk_user(
            phone=state_data.get('reg_phone'),
            email=state_data.get('reg_email'),
            first_name=state_data.get('reg_first_name'),
            last_name=state_data.get('reg_last_name'),
            user=data.get('user')
        )
    except Exception as e:
        logger.warning(f'Ошибка регистрации пользователя | {e}')
        return await message.answer('Ошибка регистрации, попробуйте позже', reply_markup=get_back_keyboard())
    await message.answer(RussianMessages().success_login.format(first_name=message.from_user.first_name), reply_markup=get_main_keyboard(True))

async def auth_phone_handler(message: Message, state: FSMContext, data) -> None:
    # await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-1)
    phone = message.text
    is_valid, phone = is_valid_phone(phone)
    if not is_valid:
        return await message.answer('Номер введен неверно, попробуйте еще раз\n\n<i>Подсказка: 79998887766</i>', reply_markup=get_cancel())
    async with AsyncAPIClient() as client:
        try:
            send_code = await client.check_phone(phone)
        except Exception as e:
            logger.warning(f'Ошибка отправки кода на телефон | {e}')
            return await message.answer('Номер введен неверно, попробуйте еще раз\n\n<i>Подсказка: 79998887766</i>', reply_markup=get_cancel())
    await state.update_data(phone=phone)
    await message.answer(RussianMessages().auth_phone_stage2, reply_markup=get_cancel())
    await state.set_state('auth:phone:sms_code')

async def auth_sms_code_handler(message: Message, state: FSMContext, data) -> None:
    # await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-1)
    sms_code = message.text
    state_data = await state.get_data()
    phone = state_data.get('phone')
    if len(sms_code) != 4:
        return await message.answer('Код введен неверно, попробуйте еще раз\n\n<i>Подсказка: xxxx</i>', reply_markup=get_cancel())
    async with AsyncAPIClient() as client:
        try:
            auth = await client.verify_phone(phone=phone, code=sms_code)
        except Exception as e:
            logger.warning(f'Ошибка авторизации | {e}')
            return await message.answer('Неверный код, попробуйте еще раз\n\n<i>Подсказка: xxxx</i>', reply_markup=get_cancel())
    await state.set_state(None)
    result = await create_new_gk_user_via_token(token=auth.get('token'), user=data.get('user'))
    if result is True:
        await message.answer(RussianMessages().success_login.format(first_name=message.from_user.first_name), reply_markup=get_main_keyboard(True))
    if result is False:
        await message.answer('<b>Неверные email или пароль. Попроуйте еще раз</b>', reply_markup=get_login_choose())
    

async def auth_email_handler(message: Message, state: FSMContext, data) -> None:
    # await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-1)
    email = message.text
    is_valid, email = is_valid_email(email)
    if not is_valid:
        return await message.answer('Email введен неверно, попробуйте еще раз\n\n<i>Подсказка: example@example.com</i>', reply_markup=get_cancel())
    await state.update_data(email=email)
    await message.answer(RussianMessages().auth_email_stage2, reply_markup=get_cancel())
    await state.set_state('auth:email:password')

async def auth_password_handler(message: Message, state: FSMContext, data) -> None:
    # await message.bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-1)
    password = message.text
    await state.update_data(password=password)
    state_data = await state.get_data()
    await state.set_state(None)
    try:
        result = await create_new_gk_user(
            email=state_data.get('email'),
            password=state_data.get('password'),
            user=data.get('user')
        )
    except Exception as e:
        logger.error(e)
        result = False

    if result is True:
        await message.answer(RussianMessages().success_login.format(first_name=message.from_user.first_name), reply_markup=get_main_keyboard(True))
    if result is False:
        await message.answer('<b>Неверные email или пароль. Попроуйте еще раз</b>', reply_markup=get_login_choose())


    