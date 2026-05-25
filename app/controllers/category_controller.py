from pathlib import Path

from fastapi import Depends, File, HTTPException, Query, Response, UploadFile, status
from fastapi.responses import HTMLResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.dependencies.auth import get_current_admin, get_current_user
from app.models.user import User
from app.schemas.category import (
    CategoryCreate,
    CategoryImageJobResponse,
    CategoryImageUploadResponse,
    CategoryListResponse,
    CategoryResponse,
    CategoryUpdate,
)
from app.services.category_service import CategoryService


class CategoryController:
    @staticmethod
    def _validate_image_file(image: UploadFile) -> None:
        if not image.filename:
            raise HTTPException(status_code=400, detail="Image filename is required")

        allowed_extensions = {".jpg", ".jpeg", ".png", ".webp"}
        extension = Path(image.filename).suffix.lower()
        if extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail="Unsupported image format. Use jpg, jpeg, png, or webp.",
            )

        content_type = image.content_type or ""
        if not content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Invalid file type. Image required.")

    @staticmethod
    def list_categories(
        search: str | None = Query(default=None, min_length=1, max_length=120),
        page: int = Query(default=1, ge=1),
        size: int = Query(default=10, ge=1, le=100),
        db: Session = Depends(get_db),
        _: User = Depends(get_current_user),
    ) -> CategoryListResponse:
        items, total = CategoryService.list_categories(db, search=search, page=page, size=size)
        return CategoryListResponse(
            items=[CategoryResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            size=size,
        )

    @staticmethod
    def create_category(
        payload: CategoryCreate,
        db: Session = Depends(get_db),
        _: User = Depends(get_current_user),
    ) -> CategoryResponse:
        if CategoryService.get_by_name(db, payload.name):
            raise HTTPException(status_code=409, detail="Category name already exists")

        try:
            category = CategoryService.create_category(db, payload)
        except IntegrityError as exc:
            db.rollback()
            raise HTTPException(status_code=409, detail="Category name already exists") from exc

        return CategoryResponse.model_validate(category)

    @staticmethod
    def update_category(
        category_id: int,
        payload: CategoryUpdate,
        db: Session = Depends(get_db),
        _: User = Depends(get_current_user),
    ) -> CategoryResponse:
        category = CategoryService.get_by_id(db, category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        if payload.name and payload.name != category.name:
            existing = CategoryService.get_by_name(db, payload.name)
            if existing:
                raise HTTPException(status_code=409, detail="Category name already exists")

        try:
            updated = CategoryService.update_category(db, category, payload)
        except IntegrityError as exc:
            db.rollback()
            raise HTTPException(status_code=409, detail="Category name already exists") from exc

        return CategoryResponse.model_validate(updated)

    @staticmethod
    def delete_category(
        category_id: int,
        db: Session = Depends(get_db),
        _: User = Depends(get_current_user),
    ) -> Response:
        category = CategoryService.get_by_id(db, category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        CategoryService.delete_category(db, category)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def upload_category_image(
        category_id: int,
        image: UploadFile = File(...),
        db: Session = Depends(get_db),
        _: User = Depends(get_current_user),
    ) -> CategoryImageUploadResponse:
        category = CategoryService.get_by_id(db, category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        CategoryController._validate_image_file(image)

        upload_dir = Path(settings.MEDIA_ROOT) / settings.MEDIA_UPLOAD_DIR
        upload_dir.mkdir(parents=True, exist_ok=True)

        extension = Path(image.filename or "").suffix.lower()
        saved_path = upload_dir / f"category_{category_id}_{Path(image.filename or 'image').stem}{extension}"

        with saved_path.open("wb") as output_file:
            output_file.write(image.file.read())

        job = CategoryService.create_image_job(db, category_id=category_id, original_image_path=str(saved_path))

        try:
            from app.workers.tasks import process_category_image

            async_result = process_category_image.delay(job.id)
            CategoryService.set_image_job_celery_id(db, job, async_result.id)
        except Exception as exc:
            CategoryService.mark_image_job_failed(db, job, f"Task enqueue failed: {exc}")
            raise HTTPException(status_code=503, detail="Failed to enqueue image processing task") from exc

        return CategoryImageUploadResponse(
            message="Image uploaded and queued for background processing",
            job=CategoryImageJobResponse.model_validate(job),
        )

    @staticmethod
    def list_image_jobs(
        status: str | None = Query(default=None, pattern="^(queued|processing|completed|failed)$"),
        category_id: int | None = Query(default=None, ge=1),
        db: Session = Depends(get_db),
        _: User = Depends(get_current_admin),
    ) -> list[CategoryImageJobResponse]:
        jobs = CategoryService.get_image_jobs(db, status=status, category_id=category_id)
        return [CategoryImageJobResponse.model_validate(job) for job in jobs]

    @staticmethod
    def retry_image_job(
        job_id: int,
        db: Session = Depends(get_db),
        _: User = Depends(get_current_admin),
    ) -> CategoryImageJobResponse:
        job = CategoryService.get_image_job_by_id(db, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Image job not found")

        if job.status not in {"failed", "completed"}:
            raise HTTPException(status_code=409, detail="Only failed/completed jobs can be retried")

        job.status = "queued"
        job.error_message = None
        db.commit()
        db.refresh(job)

        try:
            from app.workers.tasks import process_category_image

            async_result = process_category_image.delay(job.id)
            CategoryService.set_image_job_celery_id(db, job, async_result.id)
        except Exception as exc:
            CategoryService.mark_image_job_failed(db, job, f"Retry enqueue failed: {exc}")
            raise HTTPException(status_code=503, detail="Failed to retry image job") from exc

        return CategoryImageJobResponse.model_validate(job)

    @staticmethod
    def image_jobs_dashboard(_: User = Depends(get_current_admin)) -> HTMLResponse:
        html = """
<!doctype html>
<html>
<head>
  <meta charset=\"utf-8\" />
  <title>Category Image Jobs Dashboard</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #ddd; padding: 8px; }
    th { background: #f5f5f5; text-align: left; }
        .failed { color: #b71c1c; font-weight: bold; }
        .completed { color: #1b5e20; font-weight: bold; }
        .toolbar { margin-bottom: 12px; }
        input { padding: 6px; width: 480px; }
        button { padding: 6px 10px; cursor: pointer; }
  </style>
</head>
<body>
    <h2>Category Image Jobs Dashboard</h2>
    <p>Flower dashboard: <a href=\"http://localhost:5555\" target=\"_blank\">http://localhost:5555</a></p>
    <div class=\"toolbar\">
        <label>Admin Bearer Token:</label><br />
        <input id=\"token\" placeholder=\"Paste bearer token (without 'Bearer')\" />
        <button onclick=\"loadJobs()\">Load Failed Jobs</button>
    </div>

    <table>
        <thead>
            <tr>
                <th>Job ID</th>
                <th>Category ID</th>
                <th>Status</th>
                <th>Error</th>
                <th>Action</th>
            </tr>
        </thead>
        <tbody id=\"jobs\"></tbody>
    </table>

    <script>
        async function loadJobs() {
            const token = document.getElementById('token').value.trim();
            if (!token) {
                alert('Token is required');
                return;
            }

            const res = await fetch('/api/v1/admin/image-jobs?status=failed', {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (!res.ok) {
                alert('Failed to load jobs. Check token and permissions.');
                return;
            }

            const data = await res.json();
            const tbody = document.getElementById('jobs');
            tbody.innerHTML = '';

            for (const job of data) {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${job.id}</td>
                    <td>${job.category_id}</td>
                    <td class=\"${job.status}\">${job.status}</td>
                    <td>${job.error_message || ''}</td>
                    <td><button onclick=\"retryJob(${job.id})\">Retry</button></td>
                `;
                tbody.appendChild(tr);
            }
        }

        async function retryJob(jobId) {
            const token = document.getElementById('token').value.trim();
            const res = await fetch(`/api/v1/admin/image-jobs/${jobId}/retry`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (!res.ok) {
                alert('Retry failed');
                return;
            }

            await loadJobs();
        }
    </script>
</body>
</html>
"""
        return HTMLResponse(content=html)
