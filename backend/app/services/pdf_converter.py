from io import BytesIO
import pathlib
import subprocess
import sys
import tempfile
from typing import Optional

from fastapi import logger

from app.common.exceptions import TemplatePdfConvertErrorException


class PdfConverter:
    @classmethod
    def _docx_to_pdf_win32(cls, in_file: BytesIO) -> Optional[BytesIO]:
        """Файл в виде строки байт преобразуем в строку байт pdf-файла."""
        import win32com.client

        with tempfile.NamedTemporaryFile(delete=False) as output:
            docx_file = pathlib.Path(output.name).resolve()
            output.write(in_file.read())
        # docx_file.write_bytes(in_file.read())
        try:
            word = win32com.client.Dispatch("Word.Application")
            wdFormatPDF = 17
            pdf_file = docx_file.with_suffix(".pdf")
            doc = word.Documents.Open(str(docx_file))
            doc.SaveAs(str(pdf_file), FileFormat=wdFormatPDF)
            doc.Close(0)
        except Exception as e:
            docx_file.unlink(missing_ok=True)
            logger.exception("msoffice conversion failed")
            raise TemplatePdfConvertErrorException
        out_buffer = BytesIO()
        out_buffer.write(pdf_file.read_bytes())
        out_buffer.seek(0)
        docx_file.unlink(missing_ok=True)
        pdf_file.unlink(missing_ok=True)
        return out_buffer

    @classmethod
    def _docx_to_pdf_linux(cls, in_file: BytesIO) -> Optional[BytesIO]:
        """Файл в виде строки байт преобразуем в строку байт pdf-файла."""

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
                logger.exception("libreoffice conversion failed")
                raise TemplatePdfConvertErrorException
            pdf_file = out_file.with_suffix(".pdf")
            out_buffer = BytesIO()
            out_buffer.write(pdf_file.read_bytes())
            out_buffer.seek(0)
            pdf_file.unlink(missing_ok=True)
        return out_buffer

    @classmethod
    def docx_to_pdf(cls, in_file: BytesIO) -> BytesIO:
        if sys.platform == "win32":
            return cls._docx_to_pdf_win32(in_file)
        elif sys.platform == "linux":
            return cls._docx_to_pdf_linux(in_file)
        raise TemplatePdfConvertErrorException
