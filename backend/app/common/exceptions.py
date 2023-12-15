from fastapi import HTTPException, status
from app.common.constants import Messages


class TemplateException(HTTPException):
    status_code = 500
    detail = ""

    def __init__(self, detail=None):
        if detail:
            self.detail = detail
        super().__init__(status_code=self.status_code, detail=self.detail)


class TypeFieldNotFoundException(TemplateException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = Messages.TYPE_FIELD_NOT_FOUND


class TypeFieldAlreadyExistsException(TemplateException):
    status_code = status.HTTP_409_CONFLICT
    detail = Messages.TYPE_FIELD_ALREADY_EXISTS
