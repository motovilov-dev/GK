from typing import Union
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

class IsAdmin(BaseFilter):
    """Фильтр для проверки, является ли пользователь администратором"""
    def __init__(self, admin_ids: list[int]) -> None:
        self.admin_ids = admin_ids

    async def __call__(self, event: Union[Message, CallbackQuery]) -> bool:
        """Проверяет, есть ли ID пользователя в списке администраторов"""
        return event.from_user.id in self.admin_ids