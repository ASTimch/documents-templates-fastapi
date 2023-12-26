from sqladmin import Admin, ModelView
from app.models.template import (
    TemplateField,
    TemplateFieldGroup,
    TemplateFieldType,
    Template,
)
from app.models.user import User
from app.models.favorite import UserTemplateFavorite


class TemplateFieldTypeAdmin(ModelView, model=TemplateFieldType):
    column_list = [c.name for c in TemplateFieldType.__table__.c]
    name = "Тип"
    name_plural = "Типы"
    icon = "fa-solid fa-shapes"


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
    # icon = "fa-solid fa-group"


class TemplateAdmin(ModelView, model=Template):
    column_list = [c.name for c in Template.__table__.c] + [
        Template.groups,
        Template.fields,
        Template.favorited_by_users,
    ]
    name = "Шаблон"
    name_plural = "Шаблоны"
    # icon = "fa-solid fa-hotel"

    async def on_model_delete(self, model):
        # Perform some other action
        # delete docx template and thumbnail if exists
        pass


class UserAdmin(ModelView, model=User):
    # column_list = [c.name for c in Template.__table__.c] + [
    #     Template.groups,
    #     Template.fields,
    # ]
    column_list = "__all__"
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-person"

    async def on_model_delete(self, model):
        # mark User as inactive
        # log action
        pass


class UserTemplateFavoriteAdmin(ModelView, model=UserTemplateFavorite):
    column_list = "__all__"
    name = "Избранный шаблон"
    name_plural = "Избранные шаблоны"
    icon = "fa-solid fa-person"


def init_admin(app, engine):
    # admin = Admin(app, engine, authentication_backend=authentication_backend)
    admin = Admin(app, engine)
    # admin.add_view(UsersAdmin)
    admin.add_view(TemplateFieldTypeAdmin)
    admin.add_view(TemplateFieldAdmin)
    admin.add_view(TemplateFieldGroupAdmin)
    admin.add_view(TemplateAdmin)
    admin.add_view(UserAdmin)
    admin.add_view(UserTemplateFavoriteAdmin)
