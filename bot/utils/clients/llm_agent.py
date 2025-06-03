from pydantic import BaseModel
from openai import OpenAI

class Result(BaseModel):
            class Button(BaseModel):
                callback_data: str
                text: str

            answer: str
            buttons: list[Button]

class GoldenKeyAgent:
    def __init__(self):
        pass

    def get_system_prompt(self, 
                          user_info: dict,
                          user_profile: str = None,
                          users_orders: str = None,
                          user_passes: str = None,
                          services: str = None,
                          ) -> str:
        """Генерация системного промпта с информацией о пользователе и текущем времени"""
        with open('system_prompt.md', 'r') as file:
            system_prompt = file.read()
            if user_profile:
                system_prompt = system_prompt.replace('--user_profile--', user_profile)
            if users_orders:
                system_prompt = system_prompt.replace('--users_orders--', users_orders)
            if user_passes:
                system_prompt = system_prompt.replace('--user_passes--', user_passes)
            if services:
                system_prompt = system_prompt.replace('--services--', services)
        return system_prompt.replace('--user_info--', user_info)

    def ask_question(self, question: str, user_info: dict, chat_id: str, user_profile, users_orders, user_passes, services) -> Result:
        """
        Задает вопрос агенту и возвращает ответ
        
        Args:
            question: Вопрос пользователя
            user_info: Словарь с информацией о пользователе
            chat_id: Идентификатор чата для хранения истории
            
        Returns:
            Ответ агента в виде строки
        """
        # Инициализация хранилища чата и памяти
        system_prompt = self.get_system_prompt(user_info, user_profile, users_orders, user_passes, services)

        client = OpenAI(
            api_key='sk-aitunnel-C0Wxd5TZVf96WJwjJHLBWZKcM4SE2URI',
            base_url="https://api.aitunnel.ru/v1/"
        )

        MODEL = "gpt-4.1-nano"

        completion = client.beta.chat.completions.parse(
                    temperature=0.8,
                    model=MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": question},
                    ],
                    response_format=Result
                )
                
        response = completion.choices[0].message
        return response.parsed



     