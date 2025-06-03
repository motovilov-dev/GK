from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from db.models.user import GkUser
from db.models.gk_base_info import *
from utils.clients.types.passes import Pass
from typing import List, Optional
from utils.clients.types.services import RewardItem

def get_main_keyboard(gk_user: bool = False, debug: bool = False) -> InlineKeyboardMarkup:
    """Создает инлайн-клавиатуру для меню помощи"""
    keyboard = [
        [
            InlineKeyboardButton(text="🏘️ Бизнес залы", callback_data="halls:cities"),
            InlineKeyboardButton(text="🎟️ Купить визит", callback_data="passes:main"),
        ]
    ]
    if gk_user is True or debug:
        keyboard.append([InlineKeyboardButton(text="🚪 Выйти из аккаунта", callback_data="login:main")])
        keyboard.append([InlineKeyboardButton(text="🔌 Дополнительные услуги", callback_data="services:main")])
        keyboard.append([
            InlineKeyboardButton(text="👤 Профиль", callback_data="profile"),
            InlineKeyboardButton(text="🌐 QR", callback_data="qr"),
        ])
        keyboard.append([
            InlineKeyboardButton(text="💳 Заказы", callback_data="orders"),
            InlineKeyboardButton(text="📇 Визиты", callback_data="sessions:main"),
        ])
    else:
        keyboard.append([InlineKeyboardButton(text="🔑 Войти в аккаунт", callback_data="login:main")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_back_keyboard(buttons: list = None) -> InlineKeyboardMarkup:
    """Создает инлайн-клавиатуру для кнопки назад"""

    if buttons:
        keyboard = []
        keyboard.append(buttons)
        keyboard.append([InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back")])
    else:
        keyboard = [[InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_halls_cities_keyboard(cities: List[dict]) -> InlineKeyboardMarkup:
    """
    Создает инлайн-клавиатуру для выбора города с группировкой по длине названия.
    
    Города с названиями ≤6 символов группируются по 2 в строке (идут первыми),
    города с названиями >6 символов размещаются по одному в строке (идут после группированных).
    
    Args:
        cities: Список словарей с городами (должны содержать ключи 'name' и 'gk_id')
        
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками городов
    """
    keyboard = []
    
    # Разделяем города на две группы
    short_names = []  # ≤6 символов
    long_names = []   # >6 символов
    
    for city in cities:
        if len(city['name']) <= 14:
            short_names.append(city)
        else:
            long_names.append(city)
    
    # Добавляем города с короткими названиями по 2 в строку
    for i in range(0, len(short_names), 2):
        row = []
        # Первый город в паре
        city = short_names[i]
        row.append(InlineKeyboardButton(
            text=city['name'],
            callback_data=f"halls:city:{city['gk_id']}"
        ))
        
        # Второй город в паре (если есть)
        if i + 1 < len(short_names):
            city = short_names[i + 1]
            row.append(InlineKeyboardButton(
                text=city['name'],
                callback_data=f"halls:city:{city['gk_id']}"
            ))
        
        keyboard.append(row)
    
    # Добавляем города с длинными названиями по одному в строку
    for city in long_names:
        keyboard.append([InlineKeyboardButton(
            text=city['name'],
            callback_data=f"halls:city:{city['gk_id']}"
        )])
    
    # Добавляем кнопку "Назад"
    keyboard.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_hall_carousel_keyboard(halls: List[Hall], current_index: int) -> InlineKeyboardMarkup:
    """
    Создает инлайн-клавиатуру для карусели залов.
    
    Args:
        halls: Список залов
        current_index: Текущий индекс зала
        
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками навигации и подробной информации
    """
    keyboard = [
        [
            InlineKeyboardButton(text="⬅️", callback_data=f"halls:prev:{current_index}"),
            InlineKeyboardButton(text=f"{current_index + 1}/{len(halls)}", callback_data="ignore"),
            InlineKeyboardButton(text="➡️", callback_data=f"halls:next:{current_index}"),
        ],
        [
            InlineKeyboardButton(text="📝 Подробнее", callback_data=f"halls:details:{halls[current_index].gk_id}"),
        ],
        [
            InlineKeyboardButton(text="💰Купить визит", callback_data=f"passes:main"),
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад к городам", callback_data="halls:cities"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_services_carousel_keyboard(services: List[RewardItem], current_index: int, service_id: int) -> InlineKeyboardMarkup:
    """
    Создает инлайн-клавиатуру для карусели сервисов.
    
    Args:
        services: Список сервисов
        current_index: Текущий индекс сервиса
        
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками навигации и подробной информации
    """
    keyboard = [
        [
            InlineKeyboardButton(text="⬅️", callback_data=f"services:prev:{current_index}"),
            InlineKeyboardButton(text=f"{current_index + 1}/{len(services)}", callback_data="ignore"),
            InlineKeyboardButton(text="➡️", callback_data=f"services:next:{current_index}"),
        ],
        [
            InlineKeyboardButton(text='Обменять', callback_data=f'services:spend:{service_id}')
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="back"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_login_choose():
    keyboard = [
        [
            InlineKeyboardButton(text='🚪 Войти', callback_data=f'login:auth'),
            InlineKeyboardButton(text='📋 Регистрация', callback_data=f'login:register')
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="back")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_auth_choose_method():
    keyboard = [
        [
            InlineKeyboardButton(text='📞 Телефон', callback_data=f'login:auth_phone'),
            InlineKeyboardButton(text='📧 Почта', callback_data=f'login:auth_email')
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="back")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_buy_passes_keyboard(pasess_ru: List[Products], pasess_foreign: List[Products]):
    keyboard = [
        [
            InlineKeyboardButton(text='🇷🇺 Проходы РФ', callback_data=f'ignore'),
        ],
    ]
    # Group passes two per row
    for i in range(0, len(pasess_ru), 2):
        row = [
            InlineKeyboardButton(
                text=f"{pasess_ru[i].name}", 
                callback_data=f"passes:buy:{pasess_ru[i].gk_id}"
            )
        ]
        
        # Add second button if available
        if i + 1 < len(pasess_ru):
            row.append(
                InlineKeyboardButton(
                    text=f"{pasess_ru[i+1].name}",
                    callback_data=f"passes:buy:{pasess_ru[i+1].gk_id}"
                )
            )
            
        keyboard.append(row)
    keyboard.append([
        InlineKeyboardButton(text='🌍 Проходы для зарубежа', callback_data='ignore')
    ])
    # Add passes for foreign countries
    for passes in pasess_foreign:
        keyboard.append([
            InlineKeyboardButton(
                text=f"Купить {passes.count} визит(а)",
                callback_data=f"passes:buy:{passes.gk_id}"
            )
        ])
    keyboard.append([InlineKeyboardButton(text='⬅️ Назад', callback_data='back')])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_sessions_keyboard(sessions: List[Pass], current_index: int, hall_id: int):
    keyboard = [
        [
            InlineKeyboardButton(text="⬅️", callback_data=f"sessions:prev:{current_index}"),
            InlineKeyboardButton(text=f"{current_index + 1}/{len(sessions)}", callback_data="ignore"),
            InlineKeyboardButton(text="➡️", callback_data=f"sessions:next:{current_index}"),
        ],
        [
            InlineKeyboardButton(text="📝 Перейти к залу", callback_data=f"halls:details:{hall_id}"),
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="back"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_choose_banks(banks: list, call_prefix: str):
    keyboard = []
    for bank in banks:
        if bank == 'tinkoff_acquiring':
            keyboard.append([InlineKeyboardButton(text='💳 Оплата картой', callback_data=call_prefix+bank)])
        if bank == 'sber':
            keyboard.append([InlineKeyboardButton(text='Бонусы от СберСпасибо', callback_data=call_prefix+bank)])
        if bank == 'yandex-split':
            keyboard.append([InlineKeyboardButton(text='🍔 Яндекс Пэй | Сразу или частями', callback_data=call_prefix+bank)])
    keyboard.append([InlineKeyboardButton(text='⬅️ Назад', callback_data='back')])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def payment_keyboard(url: str):
    # Создаем кнопку с URL для оплаты
    keyboard = [
        [InlineKeyboardButton(text='Оплатить', url=url)],
        [InlineKeyboardButton(text='Проверить оплату', callback_data='profile')],
        [InlineKeyboardButton(text='⬅️ Назад', callback_data='back')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def back_profile():
    keyboard = [
        [InlineKeyboardButton(text='Мои промокоды', callback_data='promo')],
        [InlineKeyboardButton(text='⬅️ Назад', callback_data='profile')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def back_from_profile():
    keyboard = [
        [InlineKeyboardButton(text='Мои промокоды', callback_data='promo')],
        [InlineKeyboardButton(text='⬅️ Назад', callback_data='back')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_cancel():
    keyboard = [
        [ 
            InlineKeyboardButton(text='Отмена', callback_data='cancel')
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)