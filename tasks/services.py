from typing import Any

from projects.models import Project
from users.models import User

from .models import Comment, Task


def create_task(*, project: Project, created_by: User, **fields: Any) -> Task:
    assignees = fields.pop("assignees", None)
    task = Task.objects.create(project=project, created_by=created_by, **fields)
    if assignees is not None:
        task.assignees.set(assignees)
    return task


def update_task(task: Task, **fields: Any) -> Task:
    assignees = fields.pop("assignees", None)
    for field, value in fields.items():
        setattr(task, field, value)
    task.save()
    if assignees is not None:
        task.assignees.set(assignees)
    return task


def change_task_status(task: Task, status: str) -> Task:
    task.status = status
    task.save(update_fields=["status", "updated_at"])
    return task


def add_comment(task: Task, author: User, body: str) -> Comment:
    return Comment.objects.create(task=task, author=author, body=body)


def update_comment(comment: Comment, body: str) -> Comment:
    comment.body = body
    comment.save(update_fields=["body"])
    return comment


def delete_comment(comment: Comment) -> None:
    comment.delete()
