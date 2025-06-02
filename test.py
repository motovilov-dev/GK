import psycopg2

def get_halls_data():
    try:
        # Подключаемся к базе данных
        conn = psycopg2.connect(
            dbname="bot_db",
            user="default",
            password="Alisa220!",
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()
        
        # Выполняем запрос для получения данных залов
        query = """
        SELECT h.name, h.gk_id, h.city_gk_id, c.name as city_name 
        FROM halls h
        JOIN cities c ON h.city_uuid = c.uuid
        ORDER BY c.name, h.name
        """
        cursor.execute(query)
        
        # Формируем результат
        result = ["## Бизнес залы"]
        for hall_name, gk_id, city_gk_id, city_name in cursor.fetchall():
            line = f"- {city_name} ({hall_name}) = 'halls:details:{gk_id}:{city_gk_id}'"
            result.append(line)
            
        return "\n".join(result)
        
    except Exception as e:
        print(f"Ошибка при работе с базой данных: {e}")
        return None
    finally:
        if conn:
            conn.close()

# Получаем и выводим данные
data = get_halls_data()
if data:
    print(data)