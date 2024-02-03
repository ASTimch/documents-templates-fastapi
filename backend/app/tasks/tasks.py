import asyncio

from celery.utils.log import get_task_logger

from app.services.template import TemplateService
from app.tasks.celery_config import celery_app

logger = get_task_logger(__name__)


@celery_app.task(name="generate_template_thumbnail")
def generate_template_thumbnail(template_id: int):
    asyncio.run(TemplateService.generate_thumbnail(template_id))
    logger.info(
        "Завершена фоновая задача: "
        f"generate_template_thumbnail({template_id})"
    )


# Задел для документов
# @celery_app.task(name="generate_document_thumbnail")
# def generate_document_thumbnail(document_id: int):
#     asyncio.run(DocumentService.generate_thumbnail(document_id))
#     logger.info(
#         "Завершена фоновая задача: "
#         f"generate_document_thumbnail({document_id})"
#     )
