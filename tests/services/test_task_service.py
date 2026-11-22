from unittest.mock import Mock

import pytest

from src.models.task import TaskORM
from src.schemas.task import TaskCreateSchema, TaskSchema, TaskUpdateSchema
from src.services.task import TaskNotFoundError, TaskService


def test_list_tasks_returns_pydantic_models(
    task_service: TaskService,
    task_repository_mock: Mock,
) -> None:
    task_repository_mock.get_all.return_value = [
        TaskORM(id="task-1", title="Изучить pytest", completed=False),
        TaskORM(id="task-2", title="Написать тесты", completed=True),
    ]

    result = task_service.list_tasks()

    assert result == [
        TaskSchema(
            id="task-1",
            title="Изучить pytest",
            completed=False,
        ),
        TaskSchema(
            id="task-2",
            title="Написать тесты",
            completed=True,
        ),
    ]
    task_repository_mock.get_all.assert_called_once_with()


def test_create_task_commits(
    task_service: TaskService,
    db_mock: Mock,
    task_repository_mock: Mock,
) -> None:
    created_task = TaskORM(
        id="task-1",
        title="Новая задача",
        completed=False,
    )
    task_repository_mock.create.return_value = created_task

    result = task_service.create_task(TaskCreateSchema(title="Новая задача"))

    task_repository_mock.create.assert_called_once_with(title="Новая задача")
    db_mock.commit.assert_called_once_with()

    assert result == TaskSchema(
        id="task-1",
        title="Новая задача",
        completed=False,
    )


@pytest.mark.parametrize(
    ("payload", "expected_title", "expected_completed"),
    [
        pytest.param(
            TaskUpdateSchema(title="Новый заголовок"),
            "Новый заголовок",
            False,
            id="update-title",
        ),
        pytest.param(
            TaskUpdateSchema(completed=True),
            "Старая задача",
            True,
            id="update-completed",
        ),
        pytest.param(
            TaskUpdateSchema(title="Готово", completed=True),
            "Готово",
            True,
            id="update-all-fields",
        ),
        pytest.param(
            TaskUpdateSchema(),
            "Старая задача",
            False,
            id="no-changes",
        ),
    ],
)
def test_update_task_updates_only_passed_fields(
    task_service: TaskService,
    db_mock: Mock,
    task_repository_mock: Mock,
    payload: TaskUpdateSchema,
    expected_title: str,
    expected_completed: bool,
) -> None:
    task = TaskORM(
        id="task-1",
        title="Старая задача",
        completed=False,
    )
    task_repository_mock.get_by_id.return_value = task

    result = task_service.update_task("task-1", payload)

    task_repository_mock.get_by_id.assert_called_once_with(task_id="task-1")
    assert result == TaskSchema(
        id="task-1",
        title=expected_title,
        completed=expected_completed,
    )
    db_mock.commit.assert_called_once_with()


def test_update_task_raises_when_task_not_found(
    task_service: TaskService,
    db_mock: Mock,
    task_repository_mock: Mock,
) -> None:
    task_repository_mock.get_by_id.return_value = None

    with pytest.raises(TaskNotFoundError):
        task_service.update_task(
            "missing-task",
            TaskUpdateSchema(title="Новая задача"),
        )

    db_mock.commit.assert_not_called()


def test_delete_task_deletes_and_commits(
    task_service: TaskService,
    db_mock: Mock,
    task_repository_mock: Mock,
) -> None:
    task = TaskORM(
        id="task-1",
        title="Удалить задачу",
        completed=False,
    )
    task_repository_mock.get_by_id.return_value = task

    result = task_service.delete_task("task-1")

    assert result is None
    task_repository_mock.get_by_id.assert_called_once_with(task_id="task-1")
    task_repository_mock.delete.assert_called_once_with(task)
    db_mock.commit.assert_called_once_with()


def test_delete_task_raises_when_task_not_found(
    task_service: TaskService,
    db_mock: Mock,
    task_repository_mock: Mock,
) -> None:
    task_repository_mock.get_by_id.return_value = None

    with pytest.raises(TaskNotFoundError):
        task_service.delete_task("missing-task")

    task_repository_mock.delete.assert_not_called()
    db_mock.commit.assert_not_called()
