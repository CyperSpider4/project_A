from unittest.mock import Mock

import pytest
from sqlalchemy.orm import Session

from src.repositories.category import CategoryRepository
from src.repositories.task import TaskRepository
from src.services.category import CategoryService
from src.services.task import TaskService


@pytest.fixture
def db_mock() -> Mock:
    """Мок сессии базы данных."""
    return Mock(spec=Session)


@pytest.fixture
def category_repository_mock() -> Mock:
    """Мок репозитория категорий."""
    return Mock(spec=CategoryRepository)


@pytest.fixture
def task_repository_mock() -> Mock:
    """Мок репозитория задач."""
    return Mock(spec=TaskRepository)


@pytest.fixture
def category_service(
    db_mock: Mock,
    category_repository_mock: Mock,
) -> CategoryService:
    """Сервис категорий с замоканным репозиторием."""
    service = CategoryService(db_mock)
    service.repository = category_repository_mock
    return service


@pytest.fixture
def task_service(
    db_mock: Mock,
    task_repository_mock: Mock,
) -> TaskService:
    """Сервис задач с замоканным репозиторием."""
    service = TaskService(db_mock)
    service.repository = task_repository_mock
    return service
