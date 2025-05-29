from aiogram import F
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from typing import Union

class AuthStateFilter(BaseFilter):
    async def __call__(self, update: Union[Message, CallbackQuery], state: FSMContext) -> bool:
        current_state = await state.get_state()
        return current_state and 'auth' in current_state

class RegStateFilter(BaseFilter):
    async def __call__(self, update: Union[Message, CallbackQuery], state: FSMContext) -> bool:
        current_state = await state.get_state()
        return current_state and 'register' in current_state