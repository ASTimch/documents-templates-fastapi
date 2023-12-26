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


class TemplateNotFoundException(TemplateException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = Messages.TEMPLATE_NOT_FOUND


class TemplateFieldNotFoundException(TemplateException):
    status_code = status.HTTP_409_CONFLICT
    detail = Messages.TEMPLATE_FIELD_NOT_FOUND


class TemplateAlreadyDeletedException(TemplateException):
    status_code = status.HTTP_410_GONE
    detail = Messages.TEMPLATE_ALREADY_DELETED


class TemplateRenderErrorException(TemplateException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    detail = Messages.RENDER_ERROR


class TemplatePdfConvertErrorException(TemplateException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    detail = Messages.PDF_CONVERT_ERROR


class UserTemplateFavoriteAlreadyExistsException(TemplateException):
    status_code = status.HTTP_409_CONFLICT
    detail = Messages.FAVORITE_TEMPLATE_ALREADY_EXISTS


class UserTemplateFavoriteDoesNotExistsException(TemplateException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = Messages.FAVORITE_TEMPLATE_DOES_NOT_EXISTS
