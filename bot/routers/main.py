from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from typing import Optional
import aiohttp

from middleware.auth import AuthMiddleware
from middleware.gk_auth import GkAuthMiddleware
from keyboards.inline import *

from config import config
from messages.ru_config import RussianMessages

main_router = Router(name='main')
main_router.message.middleware(AuthMiddleware())
main_router.callback_query.middleware(AuthMiddleware())
main_router.message.middleware(GkAuthMiddleware())
main_router.callback_query.middleware(GkAuthMiddleware())

@main_router.message(Command('start'))
async def cmd_start(message: Message, state: FSMContext, **data) -> None:
    db_user = data.get('user')
    gk_auth = data.get('gk_auth')
    await state.set_state(None)
    await message.answer(
        RussianMessages().get_start_message(first_name=db_user.first_name),
        reply_markup=get_main_keyboard(gk_auth)
        )