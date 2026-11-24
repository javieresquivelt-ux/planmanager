from tasks.models import Task
from users.models import User

from .models import ProjectMembership

Role = ProjectMembership.Role

_ROLE_ORDER: dict[str, int] = {
    Role.VIEWER.value: 1,
    Role.MEMBER.value: 2,
    Role.MANAGER.value: 3,
    Role.OWNER.value: 4,
}

_MANAGER_OR_ABOVE: set[str] = {Role.MANAGER.value, Role.OWNER.value}


def role_at_least(role: str | None, minimum: str) -> bool:
    if role is None:
        return False
    return _ROLE_ORDER.get(role, 0) >= _ROLE_ORDER[minimum]


def can_view(role: str | None) -> bool:
    return role is not None


def can_create_task(role: str | None) -> bool:
    return role_at_least(role, Role.MEMBER.value)


def can_edit_task(role: str | None, task: Task, user: User) -> bool:
    if role in _MANAGER_OR_ABOVE:
        return True
    if role == Role.MEMBER.value:
        return task.created_by_id == user.id
    return False


def can_assign_task(role: str | None) -> bool:
    return role in _MANAGER_OR_ABOVE


def can_comment(role: str | None) -> bool:
    return role_at_least(role, Role.MEMBER.value)


def can_attach(role: str | None) -> bool:
    return role_at_least(role, Role.MEMBER.value)


def can_manage_members(role: str | None) -> bool:
    return role == Role.OWNER.value


def can_edit_project(role: str | None) -> bool:
    return role == Role.OWNER.value
