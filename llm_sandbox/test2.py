import json
from datetime import datetime
from typing import List, Dict, Any
import psycopg2
from schemas.home_page import *

def insert_halls_data(result: HomePage, db_connection: Dict[str, Any], schema: str = 'gk_base'):
    """Функция для вставки данных о залах в базу данных"""
    
    conn = psycopg2.connect(**db_connection)
    cursor = conn.cursor()
    
    try:
        # Вставка городов
        for hall in result.halls.data:
            if hall.cities:
                cursor.execute(
                    f"""
                    INSERT INTO {schema}.cities (id, name, code, iataCode, latitude, longitude, foreign_, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        code = EXCLUDED.code,
                        iataCode = EXCLUDED.iataCode,
                        latitude = EXCLUDED.latitude,
                        longitude = EXCLUDED.longitude,
                        foreign_ = EXCLUDED.foreign_,
                        updated_at = EXCLUDED.updated_at
                    """,
                    (
                        hall.cities.id,
                        hall.cities.name,
                        hall.cities.code,
                        hall.cities.iataCode,
                        hall.cities.latitude,
                        hall.cities.longitude,
                        hall.cities.foreign,
                        hall.cities.created_at,
                        hall.cities.updated_at
                    )
                )
        
        # Вставка типов залов
        for hall in result.halls.data:
            if hall.type_:
                cursor.execute(
                    f"""
                    INSERT INTO {schema}.hall_types (id, created_at, updated_at, name, description)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        description = EXCLUDED.description,
                        updated_at = EXCLUDED.updated_at
                    """,
                    (
                        hall.type_.id,
                        hall.type_.created_at,
                        hall.type_.updated_at,
                        hall.type_.name,
                        hall.type_.description
                    )
                )
        
        # Вставка залов
        for hall in result.halls.data:
            cursor.execute(
                f"""
                INSERT INTO {schema}.halls (
                    id, priority, name, admin_name, city_id, hall_type_id, description,
                    working_time, location, user_id, created_at, updated_at, prefix,
                    is_hidden, htype_id, station_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    priority = EXCLUDED.priority,
                    name = EXCLUDED.name,
                    admin_name = EXCLUDED.admin_name,
                    city_id = EXCLUDED.city_id,
                    hall_type_id = EXCLUDED.hall_type_id,
                    description = EXCLUDED.description,
                    working_time = EXCLUDED.working_time,
                    location = EXCLUDED.location,
                    user_id = EXCLUDED.user_id,
                    updated_at = EXCLUDED.updated_at,
                    prefix = EXCLUDED.prefix,
                    is_hidden = EXCLUDED.is_hidden,
                    htype_id = EXCLUDED.htype_id,
                    station_id = EXCLUDED.station_id
                """,
                (
                    hall.id,
                    hall.priority,
                    hall.name,
                    hall.admin_name,
                    hall.city_id,
                    hall.type_.id if hall.type_ else None,
                    hall.description,
                    hall.working_time,
                    hall.location,
                    hall.user_id,
                    hall.created_at,
                    hall.updated_at,
                    hall.prefix,
                    hall.is_hidden,
                    hall.htype_id,
                    hall.station_id
                )
            )
        
        # Вставка услуг
        for hall in result.halls.data:
            if hall.services:
                for service in hall.services:
                    cursor.execute(
                        f"""
                        INSERT INTO {schema}.services (
                            id, name, icon, type, code, text, created_at, updated_at
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO UPDATE SET
                            name = EXCLUDED.name,
                            icon = EXCLUDED.icon,
                            type = EXCLUDED.type,
                            code = EXCLUDED.code,
                            text = EXCLUDED.text,
                            updated_at = EXCLUDED.updated_at
                        """,
                        (
                            service.id,
                            service.name,
                            service.icon,
                            service.type_,
                            service.code,
                            service.text,
                            service.created_at,
                            service.updated_at
                        )
                    )
                    
                    # Связь зала с услугой
                    cursor.execute(
                        f"""
                        INSERT INTO {schema}.hall_services (hall_id, service_id)
                        VALUES (%s, %s)
                        ON CONFLICT (hall_id, service_id) DO NOTHING
                        """,
                        (hall.id, service.id)
                    )
        
        # Вставка медиа
        for hall in result.halls.data:
            if hall.media:
                for media in hall.media:
                    cursor.execute(
                        f"""
                        INSERT INTO {schema}.media (id, url, hall_id)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (id) DO UPDATE SET
                            url = EXCLUDED.url,
                            hall_id = EXCLUDED.hall_id
                        """,
                        (media.id, media.url, media.hall_id)
                    )
        
        # Вставка продуктов (regular)
        if result.products and result.products.regular:
            for product in result.products.regular:
                cursor.execute(
                    f"""
                    INSERT INTO {schema}.products_regular (
                        id, name, price, hall_id, short_description, description,
                        created_at, updated_at, registry_id, prefix, display, count, foreign_
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        price = EXCLUDED.price,
                        hall_id = EXCLUDED.hall_id,
                        short_description = EXCLUDED.short_description,
                        description = EXCLUDED.description,
                        updated_at = EXCLUDED.updated_at,
                        registry_id = EXCLUDED.registry_id,
                        prefix = EXCLUDED.prefix,
                        display = EXCLUDED.display,
                        count = EXCLUDED.count,
                        foreign_ = EXCLUDED.foreign_
                    """,
                    (
                        product.id,
                        product.name,
                        product.price,
                        product.hall_id,
                        product.short_description,
                        product.description,
                        product.created_at,
                        product.updated_at,
                        product.registry_id,
                        product.prefix,
                        product.display,
                        product.count,
                        product.foreign
                    )
                )
        
        # Вставка продуктов (foreign)
        if result.products and result.products.foreign:
            for product in result.products.foreign:
                cursor.execute(
                    f"""
                    INSERT INTO {schema}.products_foreign (
                        id, name, price, hall_id, short_description, description,
                        created_at, updated_at, registry_id, prefix, display, count, foreign_
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        price = EXCLUDED.price,
                        hall_id = EXCLUDED.hall_id,
                        short_description = EXCLUDED.short_description,
                        description = EXCLUDED.description,
                        updated_at = EXCLUDED.updated_at,
                        registry_id = EXCLUDED.registry_id,
                        prefix = EXCLUDED.prefix,
                        display = EXCLUDED.display,
                        count = EXCLUDED.count,
                        foreign_ = EXCLUDED.foreign_
                    """,
                    (
                        product.id,
                        product.name,
                        product.price,
                        product.hall_id,
                        product.short_description,
                        product.description,
                        product.created_at,
                        product.updated_at,
                        product.registry_id,
                        product.prefix,
                        product.display,
                        product.count,
                        product.foreign
                    )
                )
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

# Пример использования
if __name__ == "__main__":
    with open('response.json', 'r') as f:
        data = json.load(f)
    
    result = HomePage(**data)
    
    db_config = {
        'dbname': 'bot_db',
        'user': 'default',
        'password': 'Alisa220!',
        'host': 'localhost',
        'port': '5432'
    }
    
    insert_halls_data(result, db_config)