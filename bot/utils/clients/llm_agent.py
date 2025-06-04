from pydantic import BaseModel
from openai import OpenAI
from typing import Dict, Deque
from collections import deque
import hashlib
import json

class Result(BaseModel):
    class Button(BaseModel):
        callback_data: str
        text: str

    answer: str
    buttons: list[Button]

class GoldenKeyAgent:
    def __init__(self):
        self.chat_histories: Dict[str, Deque[dict]] = {}
        self.max_history = 2  # храним 2 последних сообщения

    def _get_chat_id(self, user_info: dict) -> str:
        """Генерирует уникальный chat_id на основе user_info"""
        # Сортируем словарь для стабильности и преобразуем в JSON строку
        sorted_info = json.dumps(user_info, sort_keys=True)
        # Создаем хеш SHA256 (можно использовать и более простой хеш)
        return hashlib.sha256(sorted_info.encode()).hexdigest()

    def _update_chat_history(self, chat_id: str, role: str, content: str):
        """Обновляет историю чата"""
        if chat_id not in self.chat_histories:
            self.chat_histories[chat_id] = deque(maxlen=self.max_history)
        self.chat_histories[chat_id].append({"role": role, "content": content})

    def get_system_prompt(self, 
                         user_info: dict,
                         user_profile: str = None,
                         users_orders: str = None,
                         user_passes: str = None,
                         services: str = None) -> str:
        """Генерация системного промпта"""
        with open('system_prompt.md', 'r') as file:
            system_prompt = file.read()
            replacements = {
                '--user_profile--': user_profile,
                '--user_orders--': users_orders,
                '--user_passes--': user_passes,
                '--services--': services
            }
            for placeholder, value in replacements.items():
                if value:
                    system_prompt = system_prompt.replace(placeholder, value)
        return system_prompt.replace('--user_info--', str(user_info))

    def ask_question(self, 
                    question: str, 
                    user_info: dict, 
                    user_profile: str = None,
                    users_orders: str = None,
                    user_passes: str = None,
                    services: str = None) -> Result | None:
        """Основной метод для вопросов к агенту"""
        # Генерируем chat_id из user_info
        chat_id = self._get_chat_id(user_info)
        
        system_prompt = self.get_system_prompt(
            user_info, user_profile, users_orders, user_passes, services
        )

        client = OpenAI(
            api_key='sk-aitunnel-C0Wxd5TZVf96WJwjJHLBWZKcM4SE2URI',
            base_url="https://api.aitunnel.ru/v1/"
        )

        MODEL = "deepseek-chat"

        # Формируем список сообщений
        messages = [{"role": "system", "content": system_prompt}]
        
        # Добавляем историю чата, если есть
        if chat_id in self.chat_histories:
            messages.extend(self.chat_histories[chat_id])
        
        # Добавляем текущий вопрос
        messages.append({"role": "user", "content": question})

        completion = client.beta.chat.completions.parse(
            temperature=0.8,
            model=MODEL,
            messages=messages,
            response_format=Result
        )
        
        response = completion.choices[0].message
        
        # Обновляем историю чата
        self._update_chat_history(chat_id, "user", question)
        self._update_chat_history(chat_id, "assistant", response.parsed.answer)
        
        return response.parsed