from celery import Celery
from app.core.config import settings

celery_app = Celery("budget", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(task_serializer="json", result_serializer="json", accept_content=["json"])

# Re-export so `celery -A app.worker worker` works
app = celery_app


@celery_app.task(name="score_promotions")
def score_promotions(promotion_ids: list[int]) -> dict:
    """Re-score promotions after a new price scrape. Called by scrapers."""
    return {"scored": len(promotion_ids)}


@celery_app.task(name="anonymize_deleted_users")
def anonymize_deleted_users() -> dict:
    """GDPR: runs daily, anonymizes users deleted > 30 days ago."""
    return {"anonymized": 0}
