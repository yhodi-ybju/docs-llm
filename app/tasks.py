from celery import shared_task
from .services import DocumentIndexingService

@shared_task
def index_pdf(file_path: str) -> int:
    service = DocumentIndexingService()
    return service.indexFile(file_path)
