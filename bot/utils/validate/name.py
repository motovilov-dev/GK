def is_valid_name(name: str) -> tuple[bool, str]:
    """
    Validates that the name consists of two parts (first and last name) in Latin characters separated by space.
    Returns tuple of (is_valid: bool, error_message: str)
    """
    # Check if empty
    if not name:
        return False, None, None, "Имя и фамилия не могут быть пустыми. \nПодсказка: используйте только буквы латинского алфавита."
        
    # Split into first and last name
    name_parts = name.split()
    if len(name_parts) != 2:
        return False, None, None, "Имя и фамилия должны быть разделены пробелом. \nПодсказка: используйте только буквы латинского алфавита."
        
    first_name, last_name = name_parts
    
    # Check if contains only Latin letters
    if not all(c.isalpha() and ord('A') <= ord(c.upper()) <= ord('Z') for c in first_name + last_name):
        return False, None, None, "Только латинские буквы разрешены в имени и фамилии. \nПодсказка: используйте только буквы латинского алфавита."
        
    return True, first_name, last_name, None
