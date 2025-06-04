import aiohttp
import asyncio
from typing import Dict, Any, Optional

from .types.auth import AuthResponse
from .types.user import UserInfoResponse
from .types.services import RewardResponse
from .types.passes import PassesResponse
from .types.orders import OrdersResponse
from .types.promo import PromoResponse


class AsyncAPIClient:
    """
    Базовый класс для асинхронного API клиента.
    """
    
    def __init__(
        self,
        base_url: str = 'http://api.dev.goldenkey.world',
        timeout: int = 10,
        token: str = None,
        headers: Optional[Dict[str, str]] = None,
        session: Optional[aiohttp.ClientSession] = None
    ):
        """
        Инициализация API клиента.
        
        :param base_url: Базовый URL API
        :param timeout: Таймаут запросов в секундах
        :param headers: Заголовки по умолчанию для запросов
        :param session: Существующая сессия aiohttp (если None - будет создана новая)
        """
        self.token = token
        self._base_url = base_url.rstrip('/')
        self._timeout = timeout
        self._headers = headers or {'Content-Type': 'application/json'}
        self._session = session
        self._own_session = session is None
        
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
        
    async def close(self) -> None:
        """Закрытие клиента (и сессии, если она была создана клиентом)"""
        if self._session is not None and self._own_session:
            await self._session.close()
            self._session = None
    
    async def _ensure_session(self) -> aiohttp.ClientSession:
        """Создает сессию, если она еще не создана"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                base_url=self._base_url,
                headers=self._headers,
                timeout=aiohttp.ClientTimeout(total=self._timeout)
            )
            self._own_session = True
        return self._session
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Any:
        """
        Базовый метод для выполнения HTTP запросов.
        
        :param method: HTTP метод (GET, POST, PUT, DELETE и т.д.)
        :param endpoint: Конечная точка API (относительный путь)
        :param params: Параметры запроса
        :param json: Тело запроса в формате JSON
        :param headers: Дополнительные заголовки запроса
        :return: Ответ от сервера (обычно JSON)
        :raises: aiohttp.ClientError при ошибках запроса
        """
        session = await self._ensure_session()
        request_headers = {**self._headers, **(headers or {})}
        
        async with session.request(
            method=method,
            url=endpoint,
            params=params,
            json=json,
            headers=request_headers
        ) as response:
            response.raise_for_status()
            return await response.json()
    
    # Примеры конкретных методов API
    
    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
        """GET запрос"""
        return await self._request('GET', endpoint, params=params, **kwargs)
    
    async def post(self, endpoint: str, json: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
        """POST запрос"""
        return await self._request('POST', endpoint, json=json, **kwargs)
    
    async def put(self, endpoint: str, json: Optional[Dict[str, Any]] = None, **kwargs) -> Any:
        """PUT запрос"""
        return await self._request('PUT', endpoint, json=json, **kwargs)
    
    async def delete(self, endpoint: str, **kwargs) -> Any:
        """DELETE запрос"""
        return await self._request('DELETE', endpoint, **kwargs)

    async def check_phone(self, phone: str, **kwargs) -> Any:
        """GET запрос"""
        return await self._request('GET', f'/api/auth/check?phone={phone}', **kwargs)

    async def verify_phone(self, phone: str, code: str, **kwargs) -> Any:
        """POST запрос"""
        return await self._request('POST', f'/api/auth/verify', json={"phone": phone, "code": code}, **kwargs)

    async def auth(self, email: str, password: str, **kwargs) -> AuthResponse:
        """
        POST запрос для аутентификации пользователя.
        
        Аргументы:
        - email: email пользователя
        - password: пароль пользователя
        - kwargs: дополнительные аргументы для запроса
        
        Возвращает:
        - AuthResponse с токеном и ID пользователя
        """
        result = await self._request(
            'POST',
            '/api/login',
            json={
                "email": email,
                "password": password,
            },
            **kwargs
        )
        self.token = result.get('token')
        return AuthResponse(**result)

    async def get_me(self, token=None, **kwargs) -> UserInfoResponse:
        """GET запрос"""
        if token:
            self.token = token
        result = await self._request(
            'GET',
            '/api/cabinet/user-info/',
            headers={'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json'}
        )
        return UserInfoResponse(**result)

    async def get_promo_services(self, **kwargs) -> RewardResponse:
        """GET запрос"""
        result = await self._request(
            'GET',
            '/api/cabinet/promo-services',
            headers={'Authorization': f'Bearer {self.token}'},
            **kwargs
        )
        return RewardResponse(**result)

    async def get_passes(self, limit: int = 30, offset: int = 0, **kwargs) -> PassesResponse:
        """GET запрос"""
        result = await self._request(
            'GET',
            f'/api/cabinet/passes?limit={limit}&offset={offset}',
            headers={'Authorization': f'Bearer {self.token}'},
            **kwargs
        )
        return PassesResponse(**result)

    async def get_bakns(self) -> Any:
        """GET запрос"""
        return await self._request(
            'GET',
            '/api/banks-list'
        )
    
    async def make_order(self, 
                         bank: str, 
                         product_id: int, 
                         email: str, 
                         quantity: int = 1,
                         installments:bool = False, 
                         mobile:bool = False,
                         promocode:str = '',
                         pay_by_act: bool = False
                         ) -> Any:
        """POST запрос"""
        result = await self._request(
            method='POST',
            endpoint='/api/order-make-land',
            json={
                "bank": bank,
                "pay_by_act": pay_by_act,
                "product_id": product_id,
                "email": email,
                "quantity": quantity,
                "installments": installments,
                "mobile": mobile,
                "promocode": promocode
            },
            headers={'Authorization': f'Bearer {self.token}'}
        )
        return result

    async def exchange_visit(self, code: str):
        """POST запрос"""
        result = await self._request(
            'POST',
            '/api/cabinet/exchange-visit',
            json={
                "services_code": code
            },
            headers={'Authorization': f'Bearer {self.token}'}
        )
        return result

    async def reg_send_code(self, phone: str):
        """POST запрос"""
        result = await self._request(
            'POST',
            '/api/send-code',
            json={
                "phone": phone
            }
        )
        return result
    
    async def reg_verify_code(self, phone: str, code: str):
        """POST запрос"""
        result = await self._request(
            'POST',
            '/api/verifyCode',
            json={
                "phone": phone,
                "code": code
            }
        )
        return result

    async def reg_final(self, 
        first_name: str,
        last_name: str, 
        email: str,
        phone: int,
        agreement: bool = True,
    ):
        """POST запрос"""
        result = await self._request(
            'POST',
            '/api/registerPhone',
            json={
                "firstname": first_name,
                "lastname": last_name,
                "email": email,
                "phone": phone,
                "agreement": agreement
            }
        )
        return result

    async def get_orders(self, limit: int = 10, offset: int = 0):
        """GET запрос"""
        result = await self._request(
           'GET',
            f'api/cabinet/orders?limit={limit}&offset={offset}',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        return OrdersResponse(**result)

    async def get_promo(self):
        """GET запрос"""
        result = await self._request(
            'GET',
            '/api/cabinet/certificates',
            headers={'Authorization': f'Bearer {self.token}'}
        )
        return PromoResponse(**result)
    
    async def add_af_card(self, card_number: int):
        """POST запрос"""
        result = await self._request(
            'POST',
            '/api/cabinet/card-af',
            headers={'Authorization': f'Bearer {self.token}'},
            json={'card': card_number}
        )
        return result


# Пример использования
# async def main():
#     # Использование контекстного менеджера
#     async with AsyncAPIClient(
#         base_url="https://api.example.com/v1",
#         headers={"Authorization": "Bearer token123"}
#     ) as client:
#         try:
#             # GET запрос
#             users = await client.get("/users", params={"limit": 10})
#             print(f"Users: {users}")
            
#             # POST запрос
#             new_user = await client.post("/users", json={"name": "John", "email": "john@example.com"})
#             print(f"Created user: {new_user}")
            
#         except aiohttp.ClientError as e:
#             print(f"API request failed: {e}")


# if __name__ == "__main__":
#     asyncio.run(main())