from fastapi import APIRouter, status
from fastapi.responses import HTMLResponse

from app.controllers.category_controller import CategoryController
from app.schemas.category import (
    CategoryImageJobResponse,
    CategoryImageUploadResponse,
    CategoryListResponse,
    CategoryResponse,
)

router = APIRouter(prefix="/categories", tags=["Categories"])
admin_router = APIRouter(prefix="/admin", tags=["Admin"])

router.get("", response_model=CategoryListResponse)(CategoryController.list_categories)
router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)(
    CategoryController.create_category
)
router.put("/{category_id}", response_model=CategoryResponse)(CategoryController.update_category)
router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)(
    CategoryController.delete_category
)
router.post("/{category_id}/image", response_model=CategoryImageUploadResponse)(
    CategoryController.upload_category_image
)

admin_router.get("/image-jobs", response_model=list[CategoryImageJobResponse])(
    CategoryController.list_image_jobs
)
admin_router.post("/image-jobs/{job_id}/retry", response_model=CategoryImageJobResponse)(
    CategoryController.retry_image_job
)
admin_router.get("/image-jobs-dashboard", response_class=HTMLResponse)(
    CategoryController.image_jobs_dashboard
)
