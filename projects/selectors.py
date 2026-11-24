from django.db.models import Count, Q, QuerySet

from tasks.models import Task
from users.models import User

from .models import Project


def projects_for_user(user: User) -> QuerySet[Project]:
    return (
        Project.objects.filter(memberships__user=user)
        .select_related("owner")
        .prefetch_related("memberships__user")
        .annotate(
            task_count=Count("tasks", distinct=True),
            done_count=Count(
                "tasks", filter=Q(tasks__status=Task.Status.DONE), distinct=True
            ),
        )
        .distinct()
        .order_by("-created_at")
    )
