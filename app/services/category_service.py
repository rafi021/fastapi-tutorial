from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.category import Category
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
