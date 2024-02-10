import urllib
from io import BytesIO

from fastapi import Response


async def get_file_response(
    file: BytesIO, filename: str, pdf: bool = False
) -> Response:
    """Формирует сообщение ответа для отправки файла.

    Args:
        file (BytesIO): файл, который должен быть отправлен.
        filename (str): наименование файла.
        pdf (bool): True для формата pdf, False для формата docx.

    Returns:
        Response: сформированный ответ.
    """
    if pdf:
        media_type = "application/pdf"
    else:
        media_type = "application/docx"
    headers = {
        "Content-Disposition": "attachment; filename*=utf-8''{}".format(
            urllib.parse.quote(filename, encoding="utf-8")
        )
    }
    return Response(file.getvalue(), headers=headers, media_type=media_type)
