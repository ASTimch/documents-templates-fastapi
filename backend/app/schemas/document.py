from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.template import id_type, template_id_type

document_id_type = Annotated[int, Field(description="Идентификатор документа")]


class DocumentReadMinifiedDTO(BaseModel):
    """Документ в сокращенном виде без полей."""

    model_config = ConfigDict(from_attributes=True)

    id: document_id_type
    description: Annotated[str, Field(description="Наименование документа")]
    template_id: template_id_type
    created_at: Annotated[datetime, Field(description="Дата создания")]
    updated_at: Annotated[datetime, Field(description="Дата модификации")]
    owner_id: Annotated[Optional[id_type], Field(description="Владелец")]
    completed: Annotated[bool, Field(description="Завершен", default=None)]
    # thumbnail: Optional[str]  # Optional[FilePath]
