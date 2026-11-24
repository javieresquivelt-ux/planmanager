from django.db.models import QuerySet

from projects.models import Project

from .models import Comment, Task


def tasks_for_project(project: Project) -> QuerySet[Task]:
    return (
        Task.objects.filter(project=project)
        .select_related("assignee", "created_by")
        .order_by("-created_at")
    )


def comments_for_task(task: Task) -> QuerySet[Comment]:
    return task.comments.select_related("author").all()
