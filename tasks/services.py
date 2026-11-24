from .models import Comment, Task


def create_task(*, project, created_by, **fields):
    return Task.objects.create(project=project, created_by=created_by, **fields)


def update_task(task, **fields):
    for field, value in fields.items():
        setattr(task, field, value)
    task.save()
    return task


def change_task_status(task, status):
    task.status = status
    task.save(update_fields=["status", "updated_at"])
    return task


def add_comment(task, author, body):
    return Comment.objects.create(task=task, author=author, body=body)
