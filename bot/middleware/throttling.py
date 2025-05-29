from typing import Any, Awaitable, Callable, Dict
from datetime import datetime
from collections import defaultdict
from datetime import timedelta

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

class ThrottlingMiddleware(BaseMiddleware):
    """Middleware для ограничения частоты запросов и прогрессивного бана"""
    def __init__(self, rate_limit: float = 0.5, minute_limit: int = 30) -> None:
        self.rate_limit = rate_limit
        self.minute_limit = minute_limit
        self.users: Dict[int, Dict[str, Any]] = defaultdict(lambda: {"date_time": datetime.now(), "first": True})
        self.request_counts: Dict[int, int] = defaultdict(int)  # Счетчик запросов в минуту
        self.ban_records: Dict[int, tuple[datetime, int]] = {}  # (время_окончания_бана, множитель)

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        """Проверяет временной интервал между запросами пользователя"""
        user_id = event.from_user.id
        now = datetime.now()

        # Проверка активного бана
        if user_id in self.ban_records:
            ban_end, multiplier = self.ban_records[user_id]
            if now < ban_end:
                remaining = (ban_end - now).seconds
                if isinstance(event, Message):
                    await event.answer(f"Вы забанены на {remaining} секунд(ы)")
                return
            else:
                del self.ban_records[user_id]

        # Подсчет запросов в минуту
        self.request_counts[user_id] += 1

        # Сброс счетчика каждую минуту
        if (now - self.users[user_id]["date_time"]).total_seconds() > 60:
            self.request_counts[user_id] = 0
            self.users[user_id]["date_time"] = now

        # Проверка аномальной активности
        if self.request_counts[user_id] > self.minute_limit:  # Лимит 5 запросов/минуту
            multiplier = self.ban_records.get(user_id, (None, 1))[1]
            ban_duration = 10 * multiplier  # Экспоненциальный рост
            self.ban_records[user_id] = (now + timedelta(seconds=ban_duration), multiplier * 2)
            
            if isinstance(event, Message):
                await event.answer(f"Превышен лимит запросов. Бан на {ban_duration} секунд")
            return

        self.users[user_id]["date_time"] = now
        return await handler(event, data)