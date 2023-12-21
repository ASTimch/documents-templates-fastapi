from sqladmin import Admin, ModelView
from app.models.template import (
    TemplateField,
    TemplateFieldGroup,
    TemplateFieldType,
    Template,
)


class TemplateFieldTypeAdmin(ModelView, model=TemplateFieldType):
    column_list = [c.name for c in TemplateFieldType.__table__.c]
    name = "Тип"
    name_plural = "Типы"
    icon = "fa-solid fa-hotel"


class TemplateFieldAdmin(ModelView, model=TemplateField):
    column_list = [c.name for c in TemplateField.__table__.c] + [
        TemplateField.type,
        TemplateField.group,
        TemplateField.template,
    ]
    column_labels = {
        TemplateField.tag: "Тэг",
        TemplateField.name: "Наименование",
        TemplateField.hint: "Подсказка",
        TemplateField.default: "Значение по умолчанию",
        TemplateField.length: "Размер",
        TemplateField.type: "Тип",
        TemplateField.group: "Группа",
        TemplateField.template: "Шаблон",
    }
    name = "Поле"
    name_plural = "Поля"
    icon = "fa-solid fa-hotel"


class TemplateFieldGroupAdmin(ModelView, model=TemplateFieldGroup):
    column_list = [c.name for c in TemplateFieldGroup.__table__.c] + [
        TemplateFieldGroup.fields,
        TemplateFieldGroup.template,
    ]
    name = "Группа"
    name_plural = "Группы"
    # icon = "fa-solid fa-hotel"


class TemplateAdmin(ModelView, model=Template):
    column_list = [c.name for c in Template.__table__.c] + [
        Template.groups,
        Template.fields,
    ]
    name = "Шаблон"
    name_plural = "Шаблоны"
    # icon = "fa-solid fa-hotel"

    async def on_model_delete(self, model):
        # Perform some other action
        # delete docx template and thumbnail if exists
        pass


# class RoomsAdmin(ModelView, model=Rooms):
#     column_list = [c.name for c in Rooms.__table__.c] + [
#         Rooms.hotel,
#         Rooms.bookings,
#     ]
#     column_labels = {
#         Rooms.hotel: "Отель",
#         Rooms.name: "Наименование",
#         Rooms.price: "Цена",
#         Rooms.description: "Описание",
#         Rooms.services: "Доп.услуги",
#         Rooms.quantity: "Количество",
#     }
#     name = "Номер"
#     name_plural = "Номера"
#     icon = "fa-solid fa-bed"


# class BookingsAdmin(ModelView, model=Bookings):
#     column_list = [c.name for c in Bookings.__table__.c] + [
#         Bookings.user,
#         Bookings.room,
#     ]
#     name = "Бронь"
#     name_plural = "Брони"
#     icon = "fa-solid fa-book"


def init_admin(app, engine):
    # admin = Admin(app, engine, authentication_backend=authentication_backend)
    admin = Admin(app, engine)
    # admin.add_view(UsersAdmin)
    admin.add_view(TemplateFieldTypeAdmin)
    admin.add_view(TemplateFieldAdmin)
    admin.add_view(TemplateFieldGroupAdmin)
    admin.add_view(TemplateAdmin)
