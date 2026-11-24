from typing import Any

from projects.models import Project
from users.models import User

from .models import Comment, Task


def create_task(*, project: Project, created_by: User, **fields: Any) -> Task:
    return Task.objects.create(project=project, created_by=created_by, **fields)


def update_task(task: Task, **fields: Any) -> Task:
    for field, value in fields.items():
        setattr(task, field, value)
    task.save()
    return task


def change_task_status(task: Task, status: str) -> Task:
    task.status = status
    task.save(update_fields=["status", "updated_at"])
    return task


def add_comment(task: Task, author: User, body: str) -> Comment:
    return Comment.objects.create(task=task, author=author, body=body)
