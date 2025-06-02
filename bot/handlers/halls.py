from db.repositories.halls_repository import HallsRepository
from db.models.gk_base_info import *
from keyboards.inline import *
from utils.messages.replace import *
from db.sessions import AsyncSessionFactory
from messages.ru_config import RussianMessages
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from loguru import logger

async def main_halls(call: CallbackQuery, state: FSMContext, data) -> None:
    db_user = data.get('user')
    query = call.data.split(':')[1]
    if query == 'cities':
        async with AsyncSessionFactory() as session:
            halls_repository = HallsRepository(session)
            cities = await halls_repository.get_all_cities()
        try:
            await call_replace_answer(
                call,
                RussianMessages().halls_cities,
                reply_markup=get_halls_cities_keyboard(cities)
            )
        except Exception as e:
            raise e
        else:
            return
    elif query in ['city', 'next', 'prev', 'details']:
        data = await state.get_data()
        if query == 'city':
            city_gk_id = int(call.data.split(':')[2])
            current_index = 0
            await state.update_data(current_hall_index=current_index, city_gk_id=city_gk_id)
        else:
            city_gk_id = data.get('city_gk_id')
            current_index = data.get('current_hall_index', 0)
        try:
            city_gk_id = int(call.data.split(':')[3])
        except Exception as e:
            pass

        async with AsyncSessionFactory() as session:
            halls_repository = HallsRepository(session)
            halls = await halls_repository.get_by_city_gk_id(city_gk_id)

        if not halls:
            logger.error(f'Ошибка выдачи залов | ID Зала {city_gk_id}')
            await call_replace_answer(call, RussianMessages().no_halls, reply_markup=get_back_keyboard())
            return

        if query == 'next':
            current_index = (int(call.data.split(':')[2]) + 1) % len(halls)
            await state.update_data(current_hall_index=current_index)
        elif query == 'prev':
            current_index = (int(call.data.split(':')[2]) - 1) % len(halls)
            await state.update_data(current_hall_index=current_index)
        elif query == 'details':
            hall_gk_id = int(call.data.split(':')[2])
            async with AsyncSessionFactory() as session:
                halls_repository = HallsRepository(session)
                hall = await halls_repository.get_by_gk_id(hall_gk_id)
            if hall:
                services_text = '\n'.join([f'✅ {service.name}' for service in hall.services]) if hall.services else 'Нет доступных услуг'
                media_group = []
                if hall.media:
                    for i, media in enumerate(hall.media):
                        media_group.append({
                            'type': 'photo',
                            'media': media.url
                        })
                        if i > 5:
                            break
                    try:
                        await call.message.delete()
                    except Exception as e:
                        pass
                    media_msg = await call.message.answer_media_group(media=media_group)
                    await call.message.answer(
                        text=RussianMessages().hall_details.format(
                                name=hall.name,
                                city=hall.city_rel.name if hall.city_rel else 'Не указано',
                                location=hall.location or 'Не указано',
                                working_time=hall.working_time or 'Не указано',
                                services=services_text
                            ),
                        reply_markup=get_back_keyboard()
                    )
                    await state.update_data(delete_media_group=media_msg)
                else:
                    await call_replace_answer(
                        call,
                        RussianMessages().hall_details.format(
                            name=hall.name,
                            city=hall.city_rel.name if hall.city_rel else 'Не указано',
                            location=hall.location or 'Не указано',
                            working_time=hall.working_time or 'Не указано',
                            services=services_text
                        ),
                        reply_markup=get_back_keyboard()
                    )
            return

        current_hall = halls[current_index]
        photo = next((media.url for media in current_hall.media), None) if current_hall.media else None

        try:
            if photo:
                await call.message.answer_photo(
                    photo=photo,
                    caption=RussianMessages().hall_card.format(
                        name=current_hall.name,
                        city=current_hall.city_rel.name if current_hall.city_rel else 'Не указано',
                        location=current_hall.location or 'Не указано',
                        working_time=current_hall.working_time or 'Не указано'
                    ),
                    reply_markup=get_hall_carousel_keyboard(halls, current_index)
                )
                await call.message.delete()
            else:
                await call_replace_answer(
                    call,
                    RussianMessages().hall_card.format(
                        name=current_hall.name,
                        city=current_hall.city_rel.name if current_hall.city_rel else 'Не указано',
                        location=current_hall.location or 'Не указано',
                        working_time=current_hall.working_time or 'Не указано'
                    ),
                    reply_markup=get_hall_carousel_keyboard(halls, current_index)
                )
        except Exception as e:
            raise e
