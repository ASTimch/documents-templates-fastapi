from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.template import id_type, template_id_type

document_id_type = Annotated[int, Field(description="Идентификатор документа")]


class DocumentFieldReadDTO(BaseModel):
    """Поле документа для чтения."""

    model_config = ConfigDict(from_attributes=True)
    id: id_type
    tag: Annotated[str, Field(description="Тэг")]
    name: Annotated[str, Field(description="Наименование")]
    hint: Annotated[str, Field(description="Подсказка")]
    type: Annotated[str, Field(description="Тип поля")]
    length: Annotated[int, Field(description="Длина поля ввода", ge=0, le=100)]
    mask: Annotated[str, Field(description="Маска валидации")]
    default: Annotated[
        Optional[str], Field(description="Значение по умолчанию", default=None)
    ]
    value: Annotated[
        Optional[str], Field(description="Значение", default=None)
    ]


class DocumentFieldWriteValueDTO(BaseModel):
    """Поле документа для записи значения."""

    model_config = ConfigDict(from_attributes=True)
    field_id: id_type
    value: Annotated[Optional[str], Field(description="Значение")]


class DocumentFieldGroupReadDTO(BaseModel):
    """Чтение группы полей документа."""

    # model_config = ConfigDict(from_attributes=True)

    id: Annotated[int, Field(description="Идентификатор группы")]
    name: Annotated[str, Field(description="Наименование группы")]
    fields: Optional[list[DocumentFieldReadDTO]]


class DocumentReadMinifiedDTO(BaseModel):
    """Документ в сокращенном виде без полей."""

    model_config = ConfigDict(from_attributes=True)

    id: document_id_type
    description: Annotated[str, Field(description="Наименование документа")]
    template_id: template_id_type
    template_title: Annotated[str, Field(description="Наименование шаблона")]
    created_at: Annotated[datetime, Field(description="Дата создания")]
    updated_at: Annotated[datetime, Field(description="Дата модификации")]
    owner_id: Annotated[Optional[id_type], Field(description="Владелец")]
    completed: Annotated[bool, Field(description="Завершен", default=None)]
    # thumbnail: Optional[str]  # Optional[FilePath]


class DocumentReadDTO(DocumentReadMinifiedDTO):
    """Чтение документа в полном виде с полями."""

    # model_config = ConfigDict(from_attributes=True)
    grouped_fields: Optional[list[DocumentFieldGroupReadDTO]]
    ungrouped_fields: Optional[list[DocumentFieldReadDTO]]


class DocumentWriteDTO(BaseModel):
    """Запись документа в полном виде с полями."""

    model_config = ConfigDict(from_attributes=True)
    description: Annotated[str, Field(description="Наименование документа")]
    template_id: template_id_type
    completed: Annotated[bool, Field(description="Завершен", default=None)]
    fields: Optional[list[DocumentFieldWriteValueDTO]]
