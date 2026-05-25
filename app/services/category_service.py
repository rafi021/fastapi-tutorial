from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.category_image_job import CategoryImageJob
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    @staticmethod
    def list_categories(
        db: Session,
        search: str | None = None,
        page: int = 1,
        size: int = 10,
    ) -> tuple[list[Category], int]:
        query = db.query(Category)

        if search:
            query = query.filter(Category.name.ilike(f"%{search}%"))

        total = query.with_entities(func.count(Category.id)).scalar() or 0
        items = (
            query.order_by(Category.id.desc())
            .offset((page - 1) * size)
            .limit(size)
            .all()
        )
        return items, total

    @staticmethod
    def create_category(db: Session, payload: CategoryCreate) -> Category:
        category = Category(name=payload.name, description=payload.description)
        db.add(category)
        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def get_by_id(db: Session, category_id: int) -> Category | None:
        return db.query(Category).filter(Category.id == category_id).first()

    @staticmethod
    def get_by_name(db: Session, name: str) -> Category | None:
        return db.query(Category).filter(Category.name == name).first()

    @staticmethod
    def update_category(db: Session, category: Category, payload: CategoryUpdate) -> Category:
        data = payload.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(category, key, value)
        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def delete_category(db: Session, category: Category) -> None:
        db.delete(category)
        db.commit()

    @staticmethod
    def create_image_job(db: Session, category_id: int, original_image_path: str) -> CategoryImageJob:
        job = CategoryImageJob(
            category_id=category_id,
            status="queued",
            original_image_path=original_image_path,
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def set_image_job_celery_id(db: Session, job: CategoryImageJob, task_id: str) -> CategoryImageJob:
        job.celery_task_id = task_id
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def get_image_job_by_id(db: Session, job_id: int) -> CategoryImageJob | None:
        return db.query(CategoryImageJob).filter(CategoryImageJob.id == job_id).first()

    @staticmethod
    def get_image_jobs(
        db: Session,
        status: str | None = None,
        category_id: int | None = None,
    ) -> list[CategoryImageJob]:
        query = db.query(CategoryImageJob)
        if status:
            query = query.filter(CategoryImageJob.status == status)
        if category_id:
            query = query.filter(CategoryImageJob.category_id == category_id)
        return query.order_by(CategoryImageJob.id.desc()).all()

    @staticmethod
    def mark_image_job_processing(db: Session, job: CategoryImageJob) -> CategoryImageJob:
        job.status = "processing"
        job.error_message = None
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def mark_image_job_completed(
        db: Session,
        job: CategoryImageJob,
        processed_image_path: str,
    ) -> CategoryImageJob:
        job.status = "completed"
        job.processed_image_path = processed_image_path
        job.error_message = None

        category = db.query(Category).filter(Category.id == job.category_id).first()
        if category:
            category.image_original_path = job.original_image_path
            category.image_processed_path = processed_image_path

        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def mark_image_job_failed(db: Session, job: CategoryImageJob, error_message: str) -> CategoryImageJob:
        job.status = "failed"
        job.error_message = error_message[:2000]
        db.commit()
        db.refresh(job)
        return job
