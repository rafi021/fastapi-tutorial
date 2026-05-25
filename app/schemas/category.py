from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    description: Optional[str] = Field(default=None, max_length=1000)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    description: Optional[str] = Field(default=None, max_length=1000)


class CategoryResponse(CategoryBase):
    id: int
    image_original_path: Optional[str] = None
    image_processed_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CategoryListResponse(BaseModel):
    items: list[CategoryResponse]
    total: int
    page: int
    size: int


class CategoryImageJobResponse(BaseModel):
    id: int
    category_id: int
    celery_task_id: Optional[str] = None
    status: str
    original_image_path: str
    processed_image_path: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CategoryImageUploadResponse(BaseModel):
    message: str
    job: CategoryImageJobResponse
