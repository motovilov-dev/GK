from email_validator import validate_email, EmailNotValidError


def is_valid_email(email: str) -> bool:
    """
    Проверяет, является ли email адрес действительным.
    :param email: Email адрес для проверки.
    :return: True, если email адрес действителен, иначе False.
    """
    try:
        # Проверяем email адрес
        emailinfo = validate_email(email, check_deliverability=False)
        email = emailinfo.normalized
        return True, email
    except EmailNotValidError:
        return False, None