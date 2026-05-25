"""add category image jobs

Revision ID: 20260526_0002
Revises: 20260526_0001
Create Date: 2026-05-26 00:30:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260526_0002"
down_revision: Union[str, Sequence[str], None] = "20260526_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("categories", sa.Column("image_original_path", sa.String(length=255), nullable=True))
    op.add_column("categories", sa.Column("image_processed_path", sa.String(length=255), nullable=True))

    op.create_table(
        "category_image_jobs",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("celery_task_id", sa.String(length=120), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("original_image_path", sa.String(length=255), nullable=False),
        sa.Column("processed_image_path", sa.String(length=255), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="CASCADE"),
    )
    op.create_index("ix_category_image_jobs_id", "category_image_jobs", ["id"])
    op.create_index("ix_category_image_jobs_category_id", "category_image_jobs", ["category_id"])
    op.create_index("ix_category_image_jobs_celery_task_id", "category_image_jobs", ["celery_task_id"])
    op.create_index("ix_category_image_jobs_status", "category_image_jobs", ["status"])


def downgrade() -> None:
    op.drop_index("ix_category_image_jobs_status", table_name="category_image_jobs")
    op.drop_index("ix_category_image_jobs_celery_task_id", table_name="category_image_jobs")
    op.drop_index("ix_category_image_jobs_category_id", table_name="category_image_jobs")
    op.drop_index("ix_category_image_jobs_id", table_name="category_image_jobs")
    op.drop_table("category_image_jobs")

    op.drop_column("categories", "image_processed_path")
    op.drop_column("categories", "image_original_path")
