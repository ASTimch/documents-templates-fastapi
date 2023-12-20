from datetime import datetime
from typing import Annotated, Optional
from fastapi import Path
from pydantic import BaseModel, ConfigDict, Field, FilePath

id_int = Annotated[int, Field(description="Идентификатор")]


class TemplateFieldTypeWriteDTO(BaseModel):
    """Тип поля шаблона - запись"""

    model_config = ConfigDict(from_attributes=True)

    type: Annotated[str, Field(description="Наименование")]
    name: Annotated[str, Field(description="Описание")]
    mask: Annotated[str, Field(description="Маска валидации", default="")]


class TemplateFieldTypeReadDTO(TemplateFieldTypeWriteDTO):
    """Тип поля шаблона - чтение"""

    id: id_int


class TemplateFieldWriteDTO(BaseModel):
    """Поле шаблона для записи"""

    model_config = ConfigDict(from_attributes=True)

    tag: Annotated[str, Field(description="Тэг")]
    name: Annotated[str, Field(description="Наименование")]
    hint: Annotated[str, Field(description="Подсказка")]
    type: Annotated[str, Field(description="Тип поля")]
    length: Annotated[int, Field(description="Длина поля ввода", ge=0, le=100)]
    default: Annotated[
        Optional[str], Field(description="Значение по умолчанию", default=None)
    ]


class TemplateFieldReadDTO(TemplateFieldWriteDTO):
    """Поле шаблона для чтения"""

    model_config = ConfigDict(from_attributes=True)

    id: id_int
    mask: Annotated[str, Field(description="Маска валидации")]


class TemplateFieldGroupReadDTO(BaseModel):
    """Группа полей шаблона"""

    # model_config = ConfigDict(from_attributes=True)

    id: Annotated[int, Field(description="Идентификатор группы")]
    name: Annotated[str, Field(description="Наименование группы")]
    fields: Optional[list[TemplateFieldReadDTO]]


class TemplateFieldGroupWriteDTO(BaseModel):
    """Группа полей шаблона - запись"""

    # model_config = ConfigDict(from_attributes=True)

    name: Annotated[str, Field(description="Наименование группы")]
    fields: Optional[list[TemplateFieldWriteDTO]]


class TemplateReadMinifiedDTO(BaseModel):
    """Шаблон в сокращенном виде без полей"""

    model_config = ConfigDict(from_attributes=True)

    id: id_int
    title: str
    description: str
    created_at: datetime
    updated_at: datetime
    deleted: bool
    category_id: Annotated[
        Optional[int], Field(title="Категория", default=None)
    ]
    owner_id: Annotated[Optional[int], Field(title="Владелец", default=None)]
    # category: Annotated[Optional[int], Field(title="Категория", default=None)]
    # owner: Annotated[Optional[int], Field(title="Владелец", default=None)]
    is_favorited: Annotated[bool, Field(title="В избранном", default=False)]
    thumbnail: Optional[str]  # Optional[FilePath]


class TemplateReadDTO(TemplateReadMinifiedDTO):
    """Шаблон в полном виде с полями"""

    # model_config = ConfigDict(from_attributes=True)

    grouped_fields: Optional[list[TemplateFieldGroupReadDTO]]
    ungrouped_fields: Optional[list[TemplateFieldReadDTO]]


class TemplateWriteDTO(BaseModel):
    """Шаблон - для записи"""

    model_config = ConfigDict(from_attributes=True)

    title: Annotated[str, Field(description="Наименование")]
    description: Annotated[str, Field(description="Описание")]
    deleted: Annotated[bool, Field(description="Удален", default=False)]
    grouped_fields: Optional[list[TemplateFieldGroupWriteDTO]]
    ungrouped_fields: Optional[list[TemplateFieldWriteDTO]]
