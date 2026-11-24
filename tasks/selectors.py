from .models import Task


def tasks_for_project(project):
    return (
        Task.objects.filter(project=project)
        .select_related("assignee", "created_by")
        .order_by("-created_at")
    )


def comments_for_task(task):
    return task.comments.select_related("author").all()
