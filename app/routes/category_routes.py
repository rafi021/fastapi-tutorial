from fastapi import APIRouter, status

from app.controllers.category_controller import CategoryController
from app.schemas.category import CategoryListResponse, CategoryResponse

router = APIRouter(prefix="/categories", tags=["Categories"])

router.get("", response_model=CategoryListResponse)(CategoryController.list_categories)
router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)(
    CategoryController.create_category
)
router.put("/{category_id}", response_model=CategoryResponse)(CategoryController.update_category)
router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)(
    CategoryController.delete_category
)
