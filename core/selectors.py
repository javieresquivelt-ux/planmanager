from typing import Any

from django.db.models import Count, OuterRef, Q, QuerySet, Subquery

from projects.models import Project, ProjectMembership
from tasks.models import Comment, Task
from users.models import User


def _count_by_field(
    qs: QuerySet[Task], field: str, choices: list[tuple[str, Any]]
) -> dict[str, int]:
    counts: dict[str, int] = {value: 0 for value, _ in choices}
    for value, total in (
        qs.values_list(field).annotate(c=Count("id")).values_list(field, "c")
    ):
        counts[value] = total
    return counts


def dashboard_metrics(user: User) -> dict[str, Any]:
    role_subquery = (
        ProjectMembership.objects.filter(project=OuterRef("pk"), user=user).values(
            "role"
        )[:1]
    )

    projects: list[Project] = list(
        Project.objects.filter(memberships__user=user)
        .select_related("owner")
        .annotate(
            user_role=Subquery(role_subquery),
            task_count=Count("tasks", distinct=True),
            done_count=Count(
                "tasks",
                filter=Q(tasks__status=Task.Status.DONE),
                distinct=True,
            ),
        )
        .order_by("-created_at")
    )

    role_labels = dict(ProjectMembership.Role.choices)
    for project in projects:
        project.user_role_label = role_labels.get(project.user_role, "")  # type: ignore[attr-defined]

    project_ids = [p.id for p in projects]

    tasks = Task.objects.filter(project_id__in=project_ids)

    tasks_by_status = _count_by_field(tasks, "status", Task.Status.choices)
    tasks_by_priority = _count_by_field(tasks, "priority", Task.Priority.choices)

    total_tasks = sum(tasks_by_status.values())
    done_tasks = tasks_by_status.get(Task.Status.DONE.value, 0)

    status_rows = [
        (label, tasks_by_status.get(value, 0)) for value, label in Task.Status.choices
    ]
    priority_rows = [
        (label, tasks_by_priority.get(value, 0))
        for value, label in Task.Priority.choices
    ]

    recent_tasks = list(tasks.select_related("project").order_by("-created_at")[:10])
    recent_comments = list(
        Comment.objects.filter(task__project_id__in=project_ids)
        .select_related("task", "task__project", "author")
        .order_by("-created_at")[:10]
    )

    return {
        "projects": projects,
        "total_projects": len(projects),
        "total_tasks": total_tasks,
        "done_tasks": done_tasks,
        "open_tasks": total_tasks - done_tasks,
        "status_rows": status_rows,
        "priority_rows": priority_rows,
        "recent_tasks": recent_tasks,
        "recent_comments": recent_comments,
    }
