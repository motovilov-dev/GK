from utils.clients.GK_ApiClient import AsyncAPIClient
from db.models.user import User, GkUser
from db.schemas.gk_user import *
from db.repositories.gk_user_repository import GkUserRepository
from db.sessions import AsyncSessionFactory
from utils.clients.types.user import UserInfoResponse
from loguru import logger

async def auth(email: str, password: str):
    async with AsyncAPIClient() as client:
        try:
            auth_data = await client.auth(email=email, password=password)
            me = await client.get_me()
            return me, auth_data
        except Exception as e:
            print(e)
            return None

async def reg_user(email: str, first_name: str, last_name: str, phone):
    async with AsyncAPIClient() as client:
        try:
            reg_data = await client.reg_final(email=email, first_name=first_name, last_name=last_name, phone=phone)
            token = reg_data.get('token')
            print(reg_data)
            me = await client.get_me(token=token)
            return me, reg_data
        except Exception as e:
            print(e)
            return None

async def reg_new_gk_user(phone, email, first_name, last_name, user: User):
    gk_user, auth_data = await reg_user(email=email, first_name=first_name, last_name=last_name, phone=phone)
    if gk_user:
        await create_gk_user(gk_user=gk_user, user=user, password='', token=auth_data.get('token'))
        return gk_user
    else:
        return None

async def create_gk_user(gk_user: UserInfoResponse, user: User, password: str, token: str):
    async with AsyncSessionFactory() as session:
        gk_user = gk_user.data
        user_repo = GkUserRepository(session)
        user_create = GkUserCreate(
            user_uuid=user.uuid,
            gk_user_id=gk_user.id,
            name=gk_user.name,
            first_name=gk_user.first_name,
            last_name=gk_user.last_name,
            email=gk_user.email,
            phone=gk_user.phone,
            password=password,
            token=token,
            role=gk_user.role.id,
            sber_id=gk_user.sber_id,
            gazprom_id=gk_user.gazprom_id,
            aeroflot_id=gk_user.aeroflot_id,
            card_id=gk_user.card_id,
            passes_amount=gk_user.passes_amount,
            user_qr=gk_user.qr
        )
        await user_repo.create(user_create)

async def create_new_gk_user(email: str, password: str, user: User):
    gk_user, auth_data = await auth(email=email, password=password)
    if not gk_user:
        return False
    try:
        await create_gk_user(gk_user=gk_user, user=user, password=password, token=auth_data.token)
    except Exception as e:
        print(e)
        return False
    else:
        return True
    

async def create_new_gk_user_via_token(token: str, user: User):
    async with AsyncAPIClient(token=token) as client:
        try:
            gk_user = await client.get_me(token=token)
        except Exception as e:
            logger.warning("Ошибка получения данных о пользователе | {e}".format(e))
            return False
    if not gk_user:
        return False
    try:
        await create_gk_user(gk_user=gk_user, user=user, password='', token=token)
    except Exception as e:
        logger.error("Ошибка создания нового GK пользователя | {}".format(e))
        return False
    else:
        return True