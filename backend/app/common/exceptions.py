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
    """Тип поля не найден в базе данных."""

    status_code = status.HTTP_404_NOT_FOUND
    detail = Messages.TYPE_FIELD_NOT_FOUND


class TypeFieldAlreadyExistsException(TemplateException):
    """Тип поля уже существует."""

    status_code = status.HTTP_409_CONFLICT
    detail = Messages.TYPE_FIELD_ALREADY_EXISTS


class TemplateNotFoundException(TemplateException):
    """Шаблон не найден."""

    status_code = status.HTTP_404_NOT_FOUND
    detail = Messages.TEMPLATE_NOT_FOUND


class TemplateFieldNotFoundException(TemplateException):
    """Поле шаблона не найдено."""

    status_code = status.HTTP_409_CONFLICT
    detail = Messages.TEMPLATE_FIELD_NOT_FOUND


class TemplateAlreadyDeletedException(TemplateException):
    """Шаблон уже помечен как удаленный."""

    status_code = status.HTTP_410_GONE
    detail = Messages.TEMPLATE_ALREADY_DELETED


class TemplateRenderErrorException(TemplateException):
    """Ошибка генерации docx документа."""

    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    detail = Messages.RENDER_ERROR


class TemplatePdfConvertErrorException(TemplateException):
    """Ошибка конвертации docx в pdf."""

    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    detail = Messages.PDF_CONVERT_ERROR


class UserTemplateFavoriteAlreadyExistsException(TemplateException):
    """Шаблон уже добавлен в избранное."""

    status_code = status.HTTP_409_CONFLICT
    detail = Messages.FAVORITE_TEMPLATE_ALREADY_EXISTS


class UserTemplateFavoriteDoesNotExistsException(TemplateException):
    """Шаблон не находится в избранном."""

    status_code = status.HTTP_404_NOT_FOUND
    detail = Messages.FAVORITE_TEMPLATE_DOES_NOT_EXISTS


class DocumentException(HTTPException):
    status_code = 500
    detail = ""

    def __init__(self, detail=None):
        if detail:
            self.detail = detail
        super().__init__(status_code=self.status_code, detail=self.detail)


class DocumentNotFoundException(DocumentException):
    """Документ не найден."""

    status_code = status.HTTP_404_NOT_FOUND
    detail = Messages.DOCUMENT_NOT_FOUND


class DocumentAccessDeniedException(DocumentException):
    """Неавторизованный доступ к документу."""

    status_code = status.HTTP_403_FORBIDDEN
    detail = Messages.ACCESS_DENIED
