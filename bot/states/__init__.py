from aiogram.fsm.state import State, StatesGroup

class UserStates(StatesGroup):
    """Группа состояний для пользовательских действий"""
    # Состояния для настроек
    SETTINGS = State()
    CHANGE_LANGUAGE = State()
    NOTIFICATIONS = State()
    
    # Состояния для профиля
    EDIT_PROFILE = State()
    ENTER_NAME = State()
    ENTER_BIO = State()
    
    # Состояния для поддержки
    SUPPORT_CHAT = State()
    FEEDBACK = State()

__all__ = ['UserStates']