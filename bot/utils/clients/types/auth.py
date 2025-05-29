from pydantic import BaseModel


class AuthResponse(BaseModel):
    """
    Модель ответа на запрос авторизации.
    Содержит:
    - token: JWT токен для аутентификации
    - user_id: идентификатор пользователя
    """
    token: str
    user_id: int

class CheckPhoneResponse(BaseModel):
    """
    Модель ответа на запрос проверки телефона.
    """
    success: bool
    data: dict