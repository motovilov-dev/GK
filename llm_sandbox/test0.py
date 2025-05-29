import json
from schemas.home_page import HomePage

with open('response.json', 'r') as f:
    data = json.load(f)

result = HomePage(**data)
# regular_products = ''
# foreign_products = ''

# for product in result.products.regular:
#     regular_products += f'''
# ### {product.name}
# * Цена: {product.price}
# * Проходов: {product.count}
# '''
# for product in result.products.foreign:
#     foreign_products += f'''
# ### {product.name}
# * Цена: {product.price}
# * Проходов: {product.count}
# '''

# products_info = f'''
# ## Продукты
# ### РФ (основные)
# {regular_products}
# ### Зарубеж 
# {foreign_products}
# '''

# with open('data/products_info.md', 'w') as f:
#     f.write(products_info)

# Обрабатываем залы и создаем файл для каждого
for hall in result.halls.data:
    # Формируем содержимое для каждого зала
    hall_services = ''
    hall_add_services = ''
    hall_media = ''
    
    for service in hall.services:
        if service.type_ == 'main':
            hall_services += f'\n* {service.name}'
        else:
            hall_add_services += f'\n* {service.name}'

    for media in hall.media:
        hall_media += f'\n* {media.url}'
    
    hall_info = f'''
### {hall.name} | {hall.cities.name}
* Время работы: {hall.working_time}
* Местоположение: {hall.location}

#### Медиа

#### Услуги{hall_services}

#### Услуги за дополнительную плату {hall_add_services if hall_add_services.__len__() > 0 else '\n---'}
'''
    
    # Создаем имя файла: убираем пробелы и спецсимволы, добавляем .md
    name = f'{hall.cities.name} | {hall.name}'
    filename = f"{name.replace(' ', '_').replace('/', '-')}.md"
    
    # Записываем информацию о зале в отдельный файл
    with open(f'data/{filename}', 'w') as f:
        f.write(hall_info)

