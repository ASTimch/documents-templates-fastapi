from typing import Final


class Messages:
    """Текстовые сообщения приложения"""

    TYPE_FIELD_NOT_FOUND: Final = "Тип поля {} не найден"
    FIELD_NOT_FOUND: Final = "Поле не найдено"
    GROUP_NOT_FOUND: Final = "Группа полей не найдена"
    TEMPLATE_NOT_FOUND: Final = "Шаблон не найден"
    DOCUMENT_NOT_FOUND: Final = "Документ не найден"

    TEMPLATE_ALREADY_DELETED: Final = "Шаблон уже удален"

    TYPE_FIELD_ALREADY_EXISTS: Final = "Тип поля {} уже существует"

    TEMPLATE_EXCESS_TAGS: Final = (
        "Шаблон содержит тэги, для которых отсутствуют поля в базе"
    )
    TEMPLATE_EXCESS_FIELDS: Final = (
        "В шаблоне отсутствуют тэги, для которых имеются поля в базе"
    )
    TEMPLATE_CONSISTENT: Final = "Шаблон и поля согласованы"
    TEMPLATE_FIELD_TAGS_ARE_NOT_UNIQUE: Final = (
        "Поля шаблона содержат неуникальные теги {}"
    )
    # TEMPLATE_GROUP_IDS_ARE_NOT_UNIQUE: Final = (
    #     "Группы полей шаблона содержат неуникальные идентификаторы id {}"
    # )
