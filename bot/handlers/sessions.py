from db.repositories.products_repository import ProductsRepository
from db.models.gk_base_info import *
from keyboards.inline import *
from utils.messages.replace import *
from db.sessions import AsyncSessionFactory
from messages.ru_config import RussianMessages
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from utils.clients.types.services import RewardResponse
from utils.clients.GK_ApiClient import AsyncAPIClient

async def main_sessions(call: CallbackQuery, state: FSMContext, data):
    query = call.data.split(':')[1]
    user = data.get('user')
    gk_user = data.get('gk_user')
    passes = []
    async with AsyncAPIClient(token=gk_user.token) as client:
        passes_response = await client.get_passes()
        passes = passes_response.data.passes

    # Проверяем, что список passes не пустой
    if not passes:
        await call.answer("У вас еще не было визитов", show_alert=True)
        return

    if query == 'main':
        msg_text = RussianMessages().sessions_main.format(
            visitor=passes[0].user_name,
            start_time=passes[0].start_time,
            status='☑️ Выполнено' if passes[0].status == 'left' else '⚠️ Ожидается',
            created_at=passes[0].created_at.strftime('%d.%m.%Y %H:%M'),
            hall=passes[0].hall.name
        )
        await state.update_data(back_data='sessions:main', back_data_name='Вернуться к проходу', city_gk_id=passes[0].hall.city_id)
        await call_replace_answer(
            call,
            msg_text,
            reply_markup=get_sessions_keyboard(passes, current_index=0, hall_id=passes[0].hall.id)
        )
    elif query in ['next', 'prev']:
        try:
            current_index = int(call.data.split(':')[2])
            
            # Корректируем индекс в зависимости от направления
            if query == 'next':
                current_index = (current_index + 1) % len(passes)
            elif query == 'prev':
                current_index = (current_index - 1) % len(passes)
            
            msg_text = RussianMessages().sessions_main.format(
                visitor=passes[current_index].user_name,
                start_time=passes[current_index].start_time,
                status='☑️ Выполнено' if passes[current_index].status == 'left' else '⚠️ Ожидается',
                created_at=passes[current_index].created_at.strftime('%d.%m.%Y %H:%M'),
                hall=passes[current_index].hall.name
            )
            await state.update_data(
                back_data=f'sessions:prev:{current_index}',
                back_data_name='Вернуться к проходу',
                city_gk_id=passes[current_index].hall.city_id
            )
            await call_replace_answer(
                call,
                msg_text,
                reply_markup=get_sessions_keyboard(passes, current_index=current_index, hall_id=passes[current_index].hall.id)
            )
        except (IndexError, ValueError) as e:
            await call.answer("Ошибка при обработке запроса")