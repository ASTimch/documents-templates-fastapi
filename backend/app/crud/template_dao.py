from datetime import date

from sqlalchemy import Result, and_, func, select, or_
from app.dao.base import BaseDAO
from app.hotels.models import Hotels
from app.bookings.models import Bookings
from app.database import async_session_maker
from app.hotels.rooms.models import Rooms
from app.hotels.schemas import SHotelRead


class HotelsDAO(BaseDAO):
    model = Hotels

    @classmethod
    async def get_busy_rooms_count(
        cls, hotel_id: int, date_from: date, date_to: date
    ):
        """
        SELECT count(*) as busy_rooms FROM bookings
            LEFT JOIN rooms ON rooms.id=bookings.room_id
            WHERE rooms.hotel_id=1
                AND ((date_from >= '2023-01-01' AND date_from <= '2023-01-10') OR
                    (date_from <= '2023-01-01' AND date_to > '2023-01-01'));
        """
        async with async_session_maker() as session:
            query = (
                select(func.count())
                .select_from(Bookings)
                .join(Rooms, Bookings.room_id == Rooms.id)
                .where(
                    and_(
                        Rooms.hotel_id == hotel_id,
                        or_(
                            and_(
                                Bookings.date_from >= date_from,
                                Bookings.date_from <= date_to,
                            ),
                            and_(
                                Bookings.date_from <= date_from,
                                Bookings.date_to > date_from,
                            ),
                        ),
                    )
                )
            )
            result: Result = await session.execute(query)
            busy_rooms: int = int(result.scalar())
            return busy_rooms

    @classmethod
    async def find_all_available(
        cls, location: str, date_from: date, date_to: date
    ):
        """
        WITH
        hotels_list AS (SELECT * FROM hotels WHERE hotels.location LIKE '%Алтай%'),
        hotel_busy_rooms AS (
            SELECT rooms.hotel_id AS hotel_id, count(*) as busy_rooms FROM bookings
            LEFT JOIN rooms ON rooms.id=bookings.room_id
            LEFT JOIN hotels ON hotels.id=rooms.hotel_id
            WHERE hotels.location LIKE '%Алтай%'
                AND ((date_from >= '2023-01-01' AND date_from <= '2023-01-10') OR
                    (date_from <= '2023-01-01' AND date_to > '2023-01-01'))
            GROUP BY rooms.hotel_id
        )
        SELECT hotels_list.id, hotels_list.name, hotels_list.location, hotels_list.services, hotels_list.rooms_quantity, hotels_list.image_id,
        (hotels_list.rooms_quantity - COALESCE(hotel_busy_rooms.busy_rooms, 0)) AS rooms_left FROM hotels_list
        LEFT OUTER JOIN hotel_busy_rooms ON hotels_list.id=hotel_busy_rooms.hotel_id;
        """
        async with async_session_maker() as session:
            hotels = select(Hotels).where(
                Hotels.location.like(f"%{location}%")
            )
            result: Result = await session.execute(hotels)
            hotels = []
            for hotel in result.scalars().all():  # type: Hotels
                busy_rooms = await HotelsDAO.get_busy_rooms_count(
                    hotel.id, date_from, date_to
                )
                rooms_left = hotel.rooms_quantity - busy_rooms
                if rooms_left > 0:
                    item = SHotelRead(
                        **hotel.__dict__,
                        rooms_left=rooms_left,
                    )
                    hotels.append(item)
            return hotels
