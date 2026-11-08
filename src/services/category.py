from sqlalchemy.orm import Session

from app.repositories.category import CategoryRepository
from app.schemas.category import Category, CategoryCreate, CategoryUpdate


class CategoryNotFoundError(Exception):
    """Категория не найдена в БД"""


class CategoryService:

    def __init__(self, db: Session):
        self.db = db
        self.repository = CategoryRepository(db)

    def list_categories(self) -> list[Category]:
        categories_orm = self.repository.get_all()
        return [Category.model_validate(c) for c in categories_orm]

    def create_category(self, category_create: CategoryCreate) -> Category:
        category_orm = self.repository.create(name=category_create.name)
        self.db.commit()
        self.db.refresh(category_orm)
        return Category.model_validate(category_orm)

    def update_category(self, category_id: str, category_update: CategoryUpdate) -> Category:
        category_for_update = self.repository.get_by_id(category_id=category_id)
        if not category_for_update:
            raise CategoryNotFoundError(f"Категория с id {category_id} не найдена")

        if category_update.name is not None:
            category_for_update.name = category_update.name

        self.db.commit()
        self.db.refresh(category_for_update)
        return Category.model_validate(category_for_update)

    def delete_category(self, category_id: str) -> None:
        category_for_delete = self.repository.get_by_id(category_id=category_id)
        if not category_for_delete:
            raise CategoryNotFoundError(f"Категория с id {category_id} не найдена")

        self.repository.delete(category_for_delete)
        self.db.commit()