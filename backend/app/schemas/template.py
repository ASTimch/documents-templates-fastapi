from datetime import datetime
from typing import Annotated, Optional
from fastapi import Path
from pydantic import BaseModel, ConfigDict, Field, FilePath

id_int = Annotated[int, Field(description="Идентификатор")]


class TemplateFieldTypeAddDTO(BaseModel):
    """Тип поля шаблона - запись"""

    model_config = ConfigDict(from_attributes=True)

    type: Annotated[str, Field(description="Наименование")]
    name: Annotated[str, Field(description="Описание")]
    mask: Annotated[str, Field(description="Маска валидации", default="")]


class TemplateFieldTypeReadDTO(TemplateFieldTypeAddDTO):
    """Тип поля шаблона - чтение"""

    id: id_int


class TemplateFieldRead(BaseModel):
    """Поле шаблона"""

    model_config = ConfigDict(from_attributes=True)

    id: id_int
    tag: Annotated[str, Field(description="Тэг")]
    name: Annotated[str, Field(description="Наименование")]
    hint: Annotated[str, Field(description="Подсказка")]
    type: Annotated[str, Field(description="Тип поля")]
    mask: Annotated[str, Field(description="Маска валидации")]
    length: Annotated[int, Field(description="Длина поля ввода")]
    default: Annotated[
        Optional[str], Field(description="Значение по умолчанию")
    ]


class TemplateFieldGroupRead(BaseModel):
    """Группа полей шаблона"""

    # model_config = ConfigDict(from_attributes=True)

    id: Annotated[int, Field(description="Идентификатор группы")]
    name: Annotated[str, Field(description="Наименование группы")]
    fields: Optional[list[TemplateFieldRead]]


class TemplateReadMinified(BaseModel):
    """Шаблон в сокращенном виде без полей"""

    model_config = ConfigDict(from_attributes=True)

    id: id_int
    title: str
    description: str
    created_at: datetime
    updated_at: datetime
    deleted: bool
    category: Optional[int]
    owner: Optional[int]
    is_favorited: Annotated[bool, Field(title="В избранном", default=False)]
    thumbnail: Optional[str]  # Optional[FilePath]


class TemplateRead(TemplateReadMinified):
    """Шаблон в полном виде с полями"""

    # model_config = ConfigDict(from_attributes=True)

    grouped_fields: Optional[list[TemplateFieldGroupRead]]
    ungrouped_fields: Optional[list[TemplateFieldRead]]
