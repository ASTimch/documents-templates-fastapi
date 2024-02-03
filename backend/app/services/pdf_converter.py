import pathlib
import subprocess
import sys
import tempfile
from io import BytesIO
from typing import Optional

from fastapi import logger
from pdf2image import convert_from_bytes
from PIL.Image import Image

from app.common.exceptions import TemplatePdfConvertErrorException


class PdfConverter:
    @classmethod
    def _docx_to_pdf_win32(cls, in_file: BytesIO) -> Optional[BytesIO]:
        """Конвертирует docx файл pdf-файла на платформах win32.

        Args:
            in_file (ByresIO): содержимое входного docx файла.

        Returns:
            BytesIO: результирующий файл в формате pdf.

        Raises:
            TemplatePdfConvertErrorException: при ошибках конвертации.
        """
        import win32com.client

        with tempfile.NamedTemporaryFile(delete=False) as output:
            docx_file = pathlib.Path(output.name).resolve()
            output.write(in_file.read())
        try:
            word = win32com.client.Dispatch("Word.Application")
            wd_format_pdf = 17
            pdf_file = docx_file.with_suffix(".pdf")
            doc = word.Documents.Open(str(docx_file))
            doc.SaveAs(str(pdf_file), FileFormat=wd_format_pdf)
            doc.Close(0)
        except Exception as e:
            docx_file.unlink(missing_ok=True)
            logger.exception(e)
            raise TemplatePdfConvertErrorException()
        out_buffer = BytesIO()
        out_buffer.write(pdf_file.read_bytes())
        out_buffer.seek(0)
        docx_file.unlink(missing_ok=True)
        pdf_file.unlink(missing_ok=True)
        return out_buffer

    @classmethod
    def _docx_to_pdf_linux(cls, in_file: BytesIO) -> Optional[BytesIO]:
        """Конвертирует docx файл pdf-файла на платформах linux.

        Для конвертации использует libreoffice.

        Args:
            in_file (ByresIO): содержимое входного docx файла.

        Returns:
            BytesIO: результирующий файл в формате pdf.

        Raises:
            TemplatePdfConvertErrorException: при ошибках конвертации.
        """
        with tempfile.NamedTemporaryFile() as output:
            out_file = pathlib.Path(output.name).resolve()
            out_file.write_bytes(in_file.read())
            try:
                subprocess.run(
                    [
                        "soffice",
                        "--headless",
                        "--invisible",
                        "--nologo",
                        "--convert-to",
                        "pdf",
                        "--outdir",
                        out_file.parent,
                        out_file.absolute(),
                    ],
                    check=True,
                )
            except Exception as e:
                logger.exception("libreoffice conversion failed" + e)
                raise TemplatePdfConvertErrorException()
            pdf_file = out_file.with_suffix(".pdf")
            out_buffer = BytesIO()
            out_buffer.write(pdf_file.read_bytes())
            out_buffer.seek(0)
            pdf_file.unlink(missing_ok=True)
        return out_buffer

    @classmethod
    def docx_to_pdf(cls, in_file: BytesIO) -> BytesIO:
        """Конвертирует docx файл pdf-файла на платформах win3/linux.

        Для конвертации win32 использует Word, для linux - libreoffice.

        Args:
            in_file (ByresIO): содержимое входного docx файла.

        Returns:
            BytesIO: результирующий файл в формате pdf.

        Raises:
            TemplatePdfConvertErrorException: при ошибках конвертации.
        """
        if sys.platform == "win32":
            return cls._docx_to_pdf_win32(in_file)
        if sys.platform == "linux":
            return cls._docx_to_pdf_linux(in_file)
        raise TemplatePdfConvertErrorException

    @classmethod
    def pdf_to_pil_thumbnail(
        cls, pdf_file: BytesIO, width: int, height: int
    ) -> Image:
        """Генерирует превью для заданного pdf файла.

        Args:
            pdf_file (BytesIO): исходный файл pdf.
            width (int), height (int): размеры результирующей картинки.
        Returns:
            PIL.Image.Image: фрагмент первой страницы заданных размеров.
        """
        images = convert_from_bytes(
            pdf_file.getvalue(),
            dpi=200,
            last_page=1,
            use_cropbox=True,
            size=(width, None),
        )
        if images:
            return images[0].crop((0, 0, width, height))
        return None

    @classmethod
    def pdf_to_thumbnail(
        cls, pdf_file: BytesIO, width: int, height: int, format: str
    ) -> BytesIO:
        """Генерирует превью для заданного pdf файла в заданном формате.

        Args:
            pdf_file (BytesIO): исходный файл pdf.
            width (int), height (int): размеры результирующей картинки.
            format (str): заданный формат результата (png, jpeg, tiff, ppm).
        Returns:
            BytesIO: картинка превью заданных размеров в нужном формате.
        """
        out_buffer = BytesIO()
        if pil_image := cls.pdf_to_pil_thumbnail(pdf_file, width, height):
            pil_image.save(out_buffer, format=format)
            out_buffer.seek(0)
        return out_buffer
