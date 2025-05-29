from typing import Optional

from typing import Tuple, Optional

def is_valid_phone(phone_number: str) -> Tuple[bool, Optional[str]]:
    """
    Проверяет, является ли номер телефона валидным.
    :param phone_number: Номер телефона в формате "7XXXXXXXXXX" или "8XXXXXXXXXX" или "+7XXXXXXXXXX".
    :return: Кортеж (bool, str), где bool - валидность номера, str - нормализованный номер (без +) или None если невалидный
    """
    # Удаляем все нецифровые символы (кроме возможного + в начале)
    cleaned = ''.join(c for c in phone_number if c.isdigit() or c == '+')
    
    # Проверяем возможные форматы начала номера
    if cleaned.startswith('+7'):
        normalized = '7' + cleaned[2:]
    elif cleaned.startswith('8'):
        normalized = '7' + cleaned[1:]
    elif cleaned.startswith('7'):
        normalized = cleaned
    else:
        return False, None
    
    # Проверяем длину и что остались только цифры
    if len(normalized) != 11 or not normalized.isdigit():
        return False, None
    
    return True, normalized
    