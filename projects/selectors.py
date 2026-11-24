from django.db.models import QuerySet

from users.models import User

from .models import Project


def projects_for_user(user: User) -> QuerySet[Project]:
    return (
        Project.objects.filter(memberships__user=user)
        .select_related("owner")
        .prefetch_related("memberships__user")
        .distinct()
        .order_by("-created_at")
    )
