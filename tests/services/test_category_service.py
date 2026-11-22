from unittest.mock import Mock

import pytest

from src.models.category import CategoryORM
from src.schemas.category import Category, CategoryCreate, CategoryUpdate
from src.services.category import CategoryNotFoundError, CategoryService


def test_list_categories_returns_pydantic_models(
    category_service: CategoryService,
    category_repository_mock: Mock,
) -> None:
    category_repository_mock.get_all.return_value = [
        CategoryORM(id="category-1", name="Работа"),
        CategoryORM(id="category-2", name="Учёба"),
    ]

    result = category_service.list_categories()

    assert result == [
        Category(id="category-1", name="Работа"),
        Category(id="category-2", name="Учёба"),
    ]
    category_repository_mock.get_all.assert_called_once_with()


def test_create_category_commits_and_refreshes(
    category_service: CategoryService,
    db_mock: Mock,
    category_repository_mock: Mock,
) -> None:
    created_category = CategoryORM(id="category-1", name="Работа")
    category_repository_mock.create.return_value = created_category

    result = category_service.create_category(CategoryCreate(name="Работа"))

    category_repository_mock.create.assert_called_once_with(name="Работа")
    db_mock.commit.assert_called_once_with()
    db_mock.refresh.assert_called_once_with(created_category)

    assert result == Category(id="category-1", name="Работа")


def test_update_category_changes_name(
    category_service: CategoryService,
    db_mock: Mock,
    category_repository_mock: Mock,
) -> None:
    category = CategoryORM(id="category-1", name="Старая категория")
    category_repository_mock.get_by_id.return_value = category

    result = category_service.update_category(
        "category-1",
        CategoryUpdate(name="Новая категория"),
    )

    category_repository_mock.get_by_id.assert_called_once_with(category_id="category-1")
    assert category.name == "Новая категория"
    assert result == Category(
        id="category-1",
        name="Новая категория",
    )
    db_mock.commit.assert_called_once_with()
    db_mock.refresh.assert_called_once_with(category)


def test_update_category_without_name_keeps_old_name(
    category_service: CategoryService,
    db_mock: Mock,
    category_repository_mock: Mock,
) -> None:
    category = CategoryORM(id="category-1", name="Работа")
    category_repository_mock.get_by_id.return_value = category

    result = category_service.update_category(
        "category-1",
        CategoryUpdate(),
    )

    assert category.name == "Работа"
    assert result.name == "Работа"
    db_mock.commit.assert_called_once_with()
    db_mock.refresh.assert_called_once_with(category)


def test_update_category_raises_when_category_not_found(
    category_service: CategoryService,
    db_mock: Mock,
    category_repository_mock: Mock,
) -> None:
    category_repository_mock.get_by_id.return_value = None

    with pytest.raises(
        CategoryNotFoundError,
        match="Категория с id missing-category не найдена",
    ):
        category_service.update_category(
            "missing-category",
            CategoryUpdate(name="Новая категория"),
        )

    db_mock.commit.assert_not_called()
    db_mock.refresh.assert_not_called()


def test_delete_category_deletes_and_commits(
    category_service: CategoryService,
    db_mock: Mock,
    category_repository_mock: Mock,
) -> None:
    category = CategoryORM(id="category-1", name="Работа")
    category_repository_mock.get_by_id.return_value = category

    result = category_service.delete_category("category-1")

    assert result is None
    category_repository_mock.get_by_id.assert_called_once_with(category_id="category-1")
    category_repository_mock.delete.assert_called_once_with(category)
    db_mock.commit.assert_called_once_with()


def test_delete_category_raises_when_category_not_found(
    category_service: CategoryService,
    db_mock: Mock,
    category_repository_mock: Mock,
) -> None:
    category_repository_mock.get_by_id.return_value = None

    with pytest.raises(
        CategoryNotFoundError,
        match="Категория с id missing-category не найдена",
    ):
        category_service.delete_category("missing-category")

    category_repository_mock.delete.assert_not_called()
    db_mock.commit.assert_not_called()
