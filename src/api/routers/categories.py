from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import get_category_service
from src.schemas.category import Category, CategoryCreate, CategoryUpdate
from src.services.category import CategoryNotFoundError, CategoryService


router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[Category])
def read_categories(category_service: CategoryService = Depends(get_category_service)) -> list[Category]:
    return category_service.list_categories()


@router.post("", response_model=Category, status_code=status.HTTP_201_CREATED)
def create_category(
    payload: CategoryCreate,
    category_service: CategoryService = Depends(get_category_service)
) -> Category:
    return category_service.create_category(category_create=payload)


@router.patch("/{category_id}", response_model=Category)
def update_category(
    category_id: str,
    payload: CategoryUpdate,
    category_service: CategoryService = Depends(get_category_service)
) -> Category:
    try:
        return category_service.update_category(category_id=category_id, category_update=payload)
    except CategoryNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Категория не найдена")


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: str, category_service: CategoryService = Depends(get_category_service)) -> None:
    try:
        category_service.delete_category(category_id=category_id)
    except CategoryNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Категория не найдена")