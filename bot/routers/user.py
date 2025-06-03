from aiogram import Router, F
from aiogram.types import URLInputFile
from aiogram.enums import ParseMode
from json import JSONDecodeError
import json

from utils.clients.llm_agent import GoldenKeyAgent
from middleware.auth import AuthMiddleware
from middleware.gk_auth import GkAuthMiddleware
from handlers.halls import *
from handlers.passes import *
from handlers.login import *
from handlers.services import *
from handlers.sessions import *
from filters.in_state import AuthStateFilter, RegStateFilter
from db.schemas.gk_user import *
from db.schemas.user import *
from utils.messages.replace import call_replace_answer

user_router = Router(name='user')
user_router.message.middleware(AuthMiddleware())
user_router.callback_query.middleware(AuthMiddleware())
user_router.message.middleware(GkAuthMiddleware())
user_router.callback_query.middleware(GkAuthMiddleware())

agent = GoldenKeyAgent()

@user_router.callback_query(F.data == 'back')
async def cmd_back(callback: CallbackQuery, state: FSMContext, **data) -> None:
    db_user = data.get('user')
    gk_auth = data.get('gk_auth')
    await state.set_state(None)
    state_data = await state.get_data()
    back_data = state_data.get('back_data')
    back_data_name = state_data.get('back_data_name')
    if back_data and back_data_name:
        media_group = state_data.get('delete_media_group')
        if media_group:
            for media in media_group:
                try:
                    await callback.bot.delete_message(
                        callback.message.chat.id,
                        media.message_id
                    )
                except Exception as e:
                    pass
        try:
            msg_text = 'Выберите действие'
            buttons = [InlineKeyboardButton(text=back_data_name, callback_data=back_data)]
            await call_replace_answer(text=msg_text, call=callback, reply_markup=get_back_keyboard(buttons))
            await state.update_data(back_data=None, back_data_name=None)
        except Exception as e:
            logger.warning(f'Ошибка возврата назад | {e}')
        else:
            return
    try:
        state_data = await state.get_data()
        media_group = state_data.get('delete_media_group')
        if media_group:
            for media in media_group:
                try:
                    await callback.bot.delete_message(
                        callback.message.chat.id,
                        media.message_id
                    )
                except Exception as e:
                    pass
        await callback.message.edit_text(
            RussianMessages().get_start_message(first_name=db_user.first_name),
            reply_markup=get_main_keyboard(gk_auth)
        )   
    except:
        state_data = await state.get_data()
        media_group = state_data.get('delete_media_group')
        if media_group:
            for media in media_group:
                try:
                    await callback.bot.delete_message(
                        callback.message.chat.id,
                        media.message_id
                    )
                except Exception as e:
                    print(e)
                    pass
        try:
            await callback.message.delete()
        except:
            pass
        await callback.message.answer(
            RussianMessages().get_start_message(first_name=db_user.first_name),
            reply_markup=get_main_keyboard(gk_auth)
        )

@user_router.callback_query(F.data.contains('halls'))
async def cmd_halls(callback: CallbackQuery, state: FSMContext, **data) -> None:
    msg_text = 'Бизнес залы'
    try:
        await main_halls(callback, state, data)
    except Exception as e:
        logger.error(f'Ошибка выдачи бизнес залов | {e}')
        await callback.message.delete()
        await callback.message.answer(
            msg_text,
            reply_markup=get_back_keyboard(),
        )

@user_router.callback_query(F.data.contains('passes'))
async def cmd_passes(callback: CallbackQuery, state: FSMContext, **data) -> None:
    msg_text = 'Проходы'
    try:
        await main_passes(callback, state, data)
    except Exception as e:
        logger.error(f'Ошибка выдачи проходов | {e}')
        await callback.message.delete()
        await callback.message.answer(
            msg_text,
            reply_markup=get_back_keyboard(),
        )

@user_router.callback_query(F.data.contains('services'))
async def cmd_halls(callback: CallbackQuery, state: FSMContext, **data) -> None:
    msg_text = 'Дополнительные услуги'
    try:
        await main_services(call=callback, state=state, data=data)
    except Exception as e:
        logger.error(f'Ошибка выдачи доп услуг | {e}')
        await callback.message.delete()
        await callback.message.answer(
            msg_text,
            reply_markup=get_back_keyboard(),
        )

@user_router.callback_query(F.data.contains('profile'))
async def cmd_halls(callback: CallbackQuery, state: FSMContext, **data) -> None:
    msg_text = 'Профиль'
    gk_user = data.get('gk_user')
    try:
        text = RussianMessages().profile.format(
            tg_id=callback.from_user.id,
            gk_id=gk_user.gk_user_id,
            card_id=gk_user.card_id,
            first_name=gk_user.first_name,
            last_name=gk_user.last_name,
            email=gk_user.email,
            phone=gk_user.phone,
            passes_amount=gk_user.passes_amount
        )
        await callback.message.edit_text(text=text, reply_markup=back_from_profile())
    except Exception as e:
        logger.error(f'Ошибка выдачи профиля | {e}')
        await callback.message.delete()
        await callback.message.answer(
            msg_text,
            reply_markup=get_back_keyboard(),
        )


@user_router.callback_query(F.data.contains('promo'))
async def cmd_promo(call: CallbackQuery, state: FSMContext, **data):
    gk_user = data.get('gk_user')
    async with AsyncAPIClient(token=gk_user.token) as client:
        try:
            promo = await client.get_promo()
        except Exception as e:
            logger.warning(f'Ошибка получения промо | {e}')
            await call.answer('Ошибка получения промокодов')
        if not promo.data.promo:
            await call.answer('У вас пока нет промокодов', show_alert=True)
            return
        promos = ''
        for item in promo.data.promo:
            promos += RussianMessages().promo_code.format(
                code=" | ".join(item.codes),  # Объединяем коды через разделитель
                service_name=item.promo_service.name,
                status='Ожидает' if item.status == 'unprocessed' else 'Активирован',
                created_at=item.created_at.strftime('%Y-%m-%d %H:%M')
            )
        await call_replace_answer(call=call, text=RussianMessages().promo.format(promos=promos), reply_markup=get_back_keyboard())


@user_router.callback_query(F.data.contains('qr'))
async def cmd_halls(call: CallbackQuery, state: FSMContext, **data) -> None:
    msg_text = 'Код'
    gk_user = data.get('gk_user')
    if not gk_user:
        await call_replace_answer(call=call, text='Вам необходимо авторизоваться', reply_markup=get_login_choose())
    try:
        # Создаем объект файла из URL
        qr_photo = URLInputFile(gk_user.user_qr)
        
        # Отправляем фото
        await call.message.delete()
        await call.message.answer_photo(
            photo=qr_photo,
            caption=f'''
<b>QR</b>
<b>Card ID:</b> <code>{gk_user.card_id}</code>
''', reply_markup=get_back_keyboard()
        )
    except Exception as e:
        logger.error(f'Ошибка выдачи QR | {e}')
        await call.message.delete()
        await call.message.answer(
            msg_text,
            reply_markup=get_back_keyboard(),
        )

@user_router.callback_query(F.data.contains('orders'))
async def cmd_halls(callback: CallbackQuery, state: FSMContext, **data) -> None:
    msg_text = 'Заказы'
    gk_user = data.get('gk_user')
    try:
        orders_txt = ''
        async with AsyncAPIClient(token=gk_user.token) as client:
            orders = await client.get_orders()
            if not orders.data:
                return await callback.answer('У вас пока нет заказов', show_alert=True)
        for order in orders.data:
            orders_txt += RussianMessages().order.format(
                order_id=order.id,
                status='⏳Ожидает' if order.status == 'pending' else '✅Оплачен' if order.status == 'completed' else '💸В обработке' if order.status == 'processing' else '⚫️Отменен',
                passes_amount=order.quantity,
                amount=order.total
            )
        await call_replace_answer(callback, RussianMessages().orders_main.format(orders=orders_txt), get_back_keyboard())

    except Exception as e:
        logger.error(f'Ошибка выдачи заказов | {e}')
        await callback.message.delete()
        await callback.message.answer(
            msg_text,
            reply_markup=get_back_keyboard(),
        )

@user_router.callback_query(F.data.contains('sessions'))
async def cmd_halls(callback: CallbackQuery, state: FSMContext, **data) -> None:
    msg_text = 'Визиты'
    try:
        await main_sessions(callback, state, data)
    except Exception as e:
        logger.error(f'Ошибка выдачи визитов | {e}')
        await callback.message.delete()
        await callback.message.answer(
            msg_text,
            reply_markup=get_back_keyboard(),
        )

@user_router.callback_query(F.data.contains('login'))
async def cmd_halls(callback: CallbackQuery, state: FSMContext, **data) -> None:
    msg_text = 'Логин'
    try:
        await main_login(callback, state, data)
    except Exception as e:
        logger.error(f'Ошибка выдачи Login | {e}')
        await callback.message.delete()
        await callback.message.answer(
            msg_text,
            reply_markup=get_back_keyboard(),
        )

@user_router.callback_query(AuthStateFilter())
async def auth_state(call: CallbackQuery, state: FSMContext, **data):
    await main_login(call, state, data)

@user_router.message(RegStateFilter())
async def reg_state(message: Message, state: FSMContext, **data):
    state_name = await state.get_state()
    try:
        stage = state_name.split(':')[1]
    except:
        stage = None
    if stage == 'phone':
        await reg_phone_handler(message=message, state=state, data=data)
    elif stage == 'sms_code':
        await reg_sms_code_handler(message=message, state=state, data=data)
    elif stage == 'name':
        await reg_name_handler(message=message, state=state, data=data)
    elif stage == 'last_name':
        await reg_last_name_handler(message=message, state=state, data=data)
    elif stage == 'email':
        await reg_email_handler(message=message, state=state, data=data)
    

@user_router.message(AuthStateFilter())
async def auth_state(message: Message, state: FSMContext, **data):
    state_name = await state.get_state()
    try:
        auth_type = state_name.split(':')[1]
    except:
        auth_type = None
    if auth_type == 'email':
        auth_stage = state_name.split(':')[2]
        if auth_stage == 'email':
            await auth_email_handler(message=message, state=state, data=data)
        elif auth_stage == 'password':
            await auth_password_handler(message=message, state=state, data=data)
    elif auth_type == 'phone':
        auth_stage = state_name.split(':')[2]
        if auth_stage == 'phone':
            await auth_phone_handler(message=message, state=state, data=data)
        elif auth_stage == 'sms_code':
            await auth_sms_code_handler(message=message, state=state, data=data)

@user_router.callback_query(F.data == 'ignore')
async def ignore_callback(callback: CallbackQuery, state: FSMContext, **data) -> None:
    await callback.answer('Информацонная кнопка')

@user_router.message(F.text)
async def handle_text(message: Message, state: FSMContext, **data) -> None:
    tg_user = data.get('user')
    gk_user = data.get('gk_user')
    gk_auth = data.get('gk_auth')
    user_info = f'''
Данные пользователя из телеграмм:
{UserBase.model_validate(tg_user, from_attributes=True).json()}

Данные пользователя из аккаунта Golden Key:
{GkUserBase.model_validate(gk_user, from_attributes=True).json() if gk_user else 'Пользователь не авторизован'}

Авторизован в аккаунте Golden Key: {gk_auth}
'''
    if gk_user:
        try:
            orders_txt = ''
            async with AsyncAPIClient(token=gk_user.token) as client:
                orders = await client.get_orders()
            if orders.data:
                for order in orders.data:
                    orders_txt += RussianMessages().order.format(
                        order_id=order.id,
                        status='⏳Ожидает' if order.status == 'pending' else '✅Оплачен' if order.status == 'completed' else '💸В обработке' if order.status == 'processing' else '⚫️Отменен',
                        passes_amount=order.quantity,
                        amount=order.total
                    )
        except Exception as e:
            orders_txt = None

        passes = None
        try:
            async with AsyncAPIClient(token=gk_user.token) as client:
                passes_response = await client.get_passes()
                passes = passes_response.data.passes
            if passes:
                passes = ''
                for pass_ in passes:
                    passes += RussianMessages().sessions_main.format(
                visitor=pass_.user_name,
                start_time=pass_.start_time,
                status='☑️ Выполнено' if pass_.status == 'left' else '⚠️ Ожидается',
                created_at=pass_.created_at.strftime('%d.%m.%Y %H:%M'),
                hall=pass_.hall.name
            )
        except Exception as e:
            passes = None

        user_profile = RussianMessages().profile.format(
            tg_id=message.from_user.id,
            gk_id=gk_user.gk_user_id,
            card_id=gk_user.card_id,
            first_name=gk_user.first_name,
            last_name=gk_user.last_name,
            email=gk_user.email,
            phone=gk_user.phone,
            passes_amount=gk_user.passes_amount
        )
        user_orders = orders_txt
        user_passes = passes
        services = None

    result = agent.ask_question(message.text, user_info, str(message.from_user.id), 
                                user_passes, user_orders, services, user_profile)
    print(result)
    try:
        message_text = result.answer
        keyboard = []
        if result.buttons:
            for button in result.buttons:
                keyboard.append([InlineKeyboardButton(text=button.text, callback_data=button.callback_data)])
            await message.answer(message_text, reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard))
        else:
            await message.answer(message_text)
    except Exception as e:
        logger.warning(e)