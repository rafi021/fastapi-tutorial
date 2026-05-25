from pathlib import Path
import shutil

from app.core.config import settings
from app.db.session import SessionLocal
from app.services.category_service import CategoryService
from app.workers.celery_app import celery_app


@celery_app.task(bind=True, name="app.workers.process_category_image", max_retries=3, default_retry_delay=30)
def process_category_image(self, job_id: int) -> dict[str, str]:
    db = SessionLocal()
    try:
        job = CategoryService.get_image_job_by_id(db, job_id)
        if not job:
            return {"status": "missing", "message": "Job not found"}

        CategoryService.mark_image_job_processing(db, job)

        original_path = Path(job.original_image_path)
        if not original_path.exists():
            CategoryService.mark_image_job_failed(db, job, "Original image file is missing")
            return {"status": "failed", "message": "Original image file is missing"}

        processed_dir = Path(settings.MEDIA_ROOT) / settings.MEDIA_PROCESSED_DIR
        processed_dir.mkdir(parents=True, exist_ok=True)

        processed_path = processed_dir / f"category_{job.category_id}_job_{job.id}{original_path.suffix}"

        # Processing step in worker context: copy original file to processed storage.
        shutil.copyfile(original_path, processed_path)

        CategoryService.mark_image_job_completed(db, job, str(processed_path))
        return {"status": "completed", "processed_path": str(processed_path)}
    except Exception as exc:
        job = CategoryService.get_image_job_by_id(db, job_id)
        if job:
            CategoryService.mark_image_job_failed(db, job, str(exc))
        raise
    finally:
        db.close()
