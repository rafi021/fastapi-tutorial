from fastapi import Depends, HTTPException, Query, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.category import (
    CategoryCreate,
    CategoryListResponse,
    CategoryResponse,
    CategoryUpdate,
)
from app.services.category_service import CategoryService


class CategoryController:
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
