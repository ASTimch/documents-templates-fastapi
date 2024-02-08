from typing import Final


class Messages:
    """Текстовые сообщения приложения"""

    TYPE_FIELD_NOT_FOUND: Final = "Тип поля {} не найден"
    FIELD_NOT_FOUND: Final = "Поле не найдено"
    GROUP_NOT_FOUND: Final = "Группа полей не найдена"
    TEMPLATE_NOT_FOUND: Final = "Шаблон не найден"
    TEMPLATE_ID_NOT_FOUND: Final = (
        "Шаблон с идентификатором {} отсутствует или удален"
    )
    DOCUMENT_NOT_FOUND: Final = "Документ не найден"
    TEMPLATE_FIELD_NOT_FOUND: Final = (
        "Поле {field_id} шаблона {template_id} не найдено"
    )

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
    ACCESS_DENIED: Final = "Доступ запрещен."

    RENDER_ERROR: Final = "Непредвиденная ошибка при генерации документа"
    PDF_CONVERT_ERROR: Final = "Непредвиденная ошибка при генерации pdf"

    FAVORITE_TEMPLATE_ALREADY_EXISTS: Final = (
        "Шаблон уже содержится в избранном"
    )
    FAVORITE_TEMPLATE_DOES_NOT_EXISTS: Final = "Шаблон не найден в избранном"
    DOCUMENT_CONFLICT: Final = "Ошибка при создании документа."
    DOCUMENT_WRONG_FIELDS: Final = (
        "Ошибка: поля {fields} не принадлежат шаблону {tpl}"
    )
