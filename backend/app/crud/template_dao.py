from datetime import date

from sqlalchemy import Result, and_, func, or_, select

from app.crud.base_dao import BaseDAO
from app.database import async_session_maker

# from app.hotels.schemas import SHotelRead
from app.models.template import (
    Template,
    TemplateField,
    TemplateFieldGroup,
    TemplateFieldType,
)


class TemplateFieldTypeDAO(BaseDAO):
    model = TemplateFieldType


class TemplateFieldGroupDAO(BaseDAO):
    model = TemplateFieldType
