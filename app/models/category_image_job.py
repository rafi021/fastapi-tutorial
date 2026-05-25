from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CategoryImageJob(Base):
    __tablename__ = "category_image_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"), index=True)
    celery_task_id: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(30), default="queued", nullable=False, index=True)
    original_image_path: Mapped[str] = mapped_column(String(255), nullable=False)
    processed_image_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
