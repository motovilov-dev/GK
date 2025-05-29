from db.repositories.products_repository import ProductsRepository
from db.models.gk_base_info import *
from keyboards.inline import *
from utils.messages.replace import *
from utils.clients.GK_ApiClient import AsyncAPIClient
from db.sessions import AsyncSessionFactory
from messages.ru_config import RussianMessages
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from loguru import logger

async def main_passes(call: CallbackQuery, state: FSMContext, data) -> None:
    """Обработчик для отображения доступных пакетов проходов"""
    db_user = data.get('user')
    gk_user = data.get('gk_user')
    query = call.data.split(':')[1]
    
    async with AsyncSessionFactory() as session:
        products_repository = ProductsRepository(session)
        products = await products_repository.get_all()
    
    # Сортируем продукты по убыванию count
    sorted_products = sorted(products, key=lambda x: x.count, reverse=False)
    
    # Разделяем на российские и зарубежные проходы
    russian_passes = [p for p in sorted_products if not p.foreign]
    foreign_passes = [p for p in sorted_products if p.foreign]

    if query == 'main':
        # Формируем текст с информацией о доступных пакетах
        passes_text = RussianMessages().available_passes
        
        # Добавляем российские проходы
        if russian_passes:
            passes_text += "\n🇷🇺 <b>Для России:</b>\n\n"
            for product in russian_passes:
                passes_text += f"📦 {product.name}\n"
                passes_text += f"💰 Стоимость: {product.price} ₽\n"
                passes_text += f"🎫 Количество проходов: {product.count}\n\n"
        
        # Добавляем зарубежные проходы
        if foreign_passes:
            passes_text += "\n🌍 <b>Для зарубежа:</b>\n\n"
            for product in foreign_passes:
                passes_text += f"📦 {product.name}\n"
                passes_text += f"💰 Стоимость: {product.price} ₽\n"
                passes_text += f"🎫 Количество проходов: {product.count}\n\n"
        
        try:
            await call_replace_answer(
                call,
                passes_text,
                reply_markup=get_buy_passes_keyboard(russian_passes, foreign_passes)
            )
        except Exception as e:
            raise e
    elif query == 'buy':
        product_id = call.data.split(':')[2]
        async with AsyncSessionFactory() as session:
            products_repository = ProductsRepository(session)
            product = await products_repository.get_by_gk_id(int(product_id))
        if not product:
            await call.answer('Проход не найден', show_alert=True)
        else:
            await state.update_data(product_id=product_id)
            async with AsyncAPIClient() as client:
                banks = await client.get_bakns()
            await call.message.edit_text(f'''
<b>Покупка прохода</b>

📦 {product.name}                            
💰 Стоимость: {product.price} ₽
🎫 Количество проходов: {product.count}

<i>Выберете банк</i>
''', reply_markup=get_choose_banks(banks=banks, call_prefix=f'passes:pay:{product_id}:'))
    
    elif query == 'pay':
        product_id = call.data.split(':')[2]
        async with AsyncSessionFactory() as session:
            products_repository = ProductsRepository(session)
            product = await products_repository.get_by_gk_id(int(product_id))
        if not product:
            await call.answer('Проход не найден', show_alert=True)
        bank = call.data.split(':')[3]
        async with AsyncAPIClient(token=gk_user.token) as client:
            try:
                make_order = await client.make_order(
                    bank=bank, 
                    product_id=product_id, 
                    email=gk_user.email
                )
            except Exception as e:
                logger.warning(f'Ошибка при создании платежной ссылки | {e}')
                return await call.message.edit_text('Произошла ошибка, попробуйте позже')
            else:
                return await call.message.edit_text(f'''
<b>Покупка прохода</b>

📦 {product.name}                            
💰 Стоимость: {product.price} ₽
🎫 Количество проходов: {product.count}

<i>Оплатите покупку</i>
''', reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton('Оплатить', url=make_order.get('data'))], [InlineKeyboardButton('⬅️ Назад', 'back')]]))

        
