from keyboards.inline import *
from messages.ru_config import RussianMessages
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from utils.clients.GK_ApiClient import AsyncAPIClient
from loguru import logger

async def main_services(call: CallbackQuery, state: FSMContext, data) -> None:
    gk_user = data.get('gk_user')
    user = data.get('user')
    query = call.data.split(':')[1]
    async with AsyncAPIClient(token=gk_user.token) as client:
        promo_services = await client.get_promo_services()
        promo_services = promo_services.data
    if query == 'main':
        await call.message.edit_text(
            RussianMessages().service.format(
                name=promo_services[0].name,
                description=promo_services[0].description,
                denomination=promo_services[0].denomination,
                passes_amount=gk_user.passes_amount
            ),
            reply_markup=get_services_carousel_keyboard(promo_services, 0, promo_services[0].id)
        )
    elif query in ['next', 'prev']:
        if query == 'next':
            current_index = (int(call.data.split(':')[2]) + 1) % len(promo_services)
            await call.message.edit_text(
                RussianMessages().service.format(
                    name=promo_services[current_index].name,
                    description=promo_services[current_index].description,
                    denomination=promo_services[current_index].denomination,
                    passes_amount=gk_user.passes_amount
                ),
                reply_markup=get_services_carousel_keyboard(promo_services, current_index, promo_services[current_index].id)
            )
        elif query == 'prev':
            current_index = (int(call.data.split(':')[2]) - 1) % len(promo_services)
            await call.message.edit_text(
                RussianMessages().service.format(
                    name=promo_services[current_index].name,
                    description=promo_services[current_index].description,
                    denomination=promo_services[current_index].denomination,
                    passes_amount=gk_user.passes_amount
                ),
                reply_markup=get_services_carousel_keyboard(promo_services, current_index, promo_services[current_index].id)
            )
    elif query in ['spend']:
        service_id = int(call.data.split(':')[2])
        if gk_user.passes_amount <= 0:
            return await call.answer('Недостаточно проходов для обмена', show_alert=True)
        promo_service = next((item for item in promo_services if item.id == service_id), None)
        if not promo_service:
            return await call.answer('Промокод не найден')
        async with AsyncAPIClient(token=gk_user.token) as client:
            try: 
                result = await client.exchange_visit(promo_service.code)
                print(result)
            except Exception as e:
                logger.warning(f'Ошибка при обмене на промокод | {e}')
                return await call.answer('Ошибка обмена')
        await call.message.edit_reply_markup(reply_markup=None)
        await call.message.answer('Успешно! Промокод уже отправлен вам на почту!', reply_markup=back_profile())
        return await call.answer('Успешно! Промокод уже отправлен вам на почту!', show_alert=True)





