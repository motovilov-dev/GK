from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Создает основную клавиатуру бота"""
    keyboard = [
        [KeyboardButton(text="👤 Профиль"), KeyboardButton(text="⚙️ Настройки")],
        [KeyboardButton(text="ℹ️ Помощь")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие"
    )

def get_settings_keyboard() -> ReplyKeyboardMarkup:
    """Создает клавиатуру настроек"""
    keyboard = [
        [KeyboardButton(text="🔔 Уведомления"), KeyboardButton(text="🌍 Язык")],
        [KeyboardButton(text="⬅️ Назад")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Настройки"
    )