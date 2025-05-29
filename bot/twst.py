from db.sessions import AsyncSessionFactory
import json
from db.schemas.halls_validate import HomePage
from db.models.gk_base_info import *

with open('response.json', 'r') as f:
    data = json.load(f)

result = HomePage(**data)

# async def main():
#     async with AsyncSessionFactory() as session:
#         for hall in result.halls.data:
#             city_db = City(
#                 gk_id=hall.cities.id,
#                 name=hall.cities.name,
#                 code=hall.cities.code,
#                 foreign=hall.cities.foreign,
#             )
#             session.add(city_db)
#             await session.flush()

#             hall_db = Hall(
#                 gk_id=hall.id,
#                 name=hall.name,
#                 admin_name=hall.admin_name,
#                 working_time=hall.working_time,
#                 location=hall.location,
#                 is_hidden=hall.is_hidden,
#                 htype_id=hall.htype_id,
#                 station_id=hall.station_id,
#                 city_uuid=city_db.uuid,
#                 city_gk_id=hall.cities.id,
#                 city=hall.cities.name
#             )
#             session.add(hall_db)
#             await session.flush()

#             for media in hall.media:
#                 media_db = Media(
#                     hall_uuid=hall_db.uuid,
#                     gk_id=media.id,
#                     hall_gk_id=hall.id,
#                     url=media.url,
#                 )
#                 session.add(media_db)
#                 await session.flush()

#             for service in hall.services:
#                 service_db = Services(
#                     hall_uuid=hall_db.uuid,
#                     hall_gk_id=hall.id,
#                     gk_id=service.id,
#                     name=service.name,
#                     text=service.text,
#                     icon_url=service.icon,
#                     service_type=service.type_,
#                     content=service.content,
#                 )
#                 session.add(service_db)
#                 await session.flush()
#         await session.commit()


async def main():
    async with AsyncSessionFactory() as session:
        # for product in result.products.regular:
        #     product_db = Products(
        #         gk_id=product.id,
        #         name=product.name,
        #         price=product.price, 
        #         prefix=product.prefix,
        #         display=product.display,
        #         count=product.count,
        #         foreign=product.foreign
        #     )
        #     session.add(product_db)
        for product in result.products.foreign:
            product_db = Products(
                gk_id=product.id,
                name=product.name,
                price=product.price, 
                prefix=product.prefix,
                display=product.display,
                count=product.count,
                foreign=product.foreign
            )
            session.add(product_db)
        await session.commit()


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())