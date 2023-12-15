# import codecs
# import csv
# import io
# import json
# from typing import Annotated, Any, BinaryIO

# from fastapi import APIRouter, Depends, HTTPException, Path, UploadFile
# from sqlalchemy import insert
# from app.bookings.models import Bookings

# from app.bookings.schemas import SNewBooking
# from app.database import async_session_maker
# from app.common.exceptions import ImportInvalidTableNameException
# from app.hotels.dao import HotelsDAO
# from app.hotels.rooms.dao import RoomsDAO
# from app.hotels.rooms.schemas import SRoom
# from app.hotels.schemas import SHotelWrite
# from app.users.dependencies import get_current_user
# from app.users.models import Users

# router_import = APIRouter(prefix="/import", tags=["Импорт"])


# async def load_field_types(file: BinaryIO):
#     json_objects = json.load(file)
#     schema_objects = []
#     json_reader = csv.DictReader(codecs.iterdecode(file.file, "utf-8"))
#     for row in csv_reader:
#         row["services"] = json.loads(row["services"].replace("'", '"'))
#         obj = SHotelWrite(**row)
#         await HotelsDAO.add(**obj.model_dump())


# # async def upload_rooms(file: UploadFile):
# #     csv_reader = csv.DictReader(codecs.iterdecode(file.file, "utf-8"))
# #     for row in csv_reader:
# #         row["services"] = json.loads(row["services"].replace("'", '"'))
# #         obj = SRoom(**row)
# #         await RoomsDAO.add(**obj.model_dump())
