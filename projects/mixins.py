from typing import Any, cast

from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpRequest
from django.shortcuts import get_object_or_404

from users.models import User

from .models import Project, ProjectMembership


class ProjectAccessMixin:
    project_kwarg: str = "project_pk"
    request: HttpRequest
    kwargs: dict[str, Any]
    _project: Project | None = None
    _role: str | None = None

    def get_project(self) -> Project:
        project = self._project
        if project is None:
            project = get_object_or_404(
                Project, pk=self.kwargs[self.project_kwarg]
            )
            self._project = project
        return project

    def get_role(self) -> str | None:
        if self.request.user.is_superuser:
            return ProjectMembership.Role.OWNER.value
        role = self._role
        if role is None:
            role = ProjectMembership.get_role(
                cast(User, self.request.user), self.get_project()
            )
            self._role = role
        return role


class ProjectMemberRequiredMixin(ProjectAccessMixin, UserPassesTestMixin):
    """Cualquier miembro del proyecto (VIEWER o superior)."""

    def test_func(self) -> bool:
        return self.get_role() is not None


class ProjectManagerRequiredMixin(ProjectAccessMixin, UserPassesTestMixin):
    """MANAGER u OWNER."""

    def test_func(self) -> bool:
        return self.get_role() in {
            ProjectMembership.Role.MANAGER.value,
            ProjectMembership.Role.OWNER.value,
        }


class ProjectOwnerRequiredMixin(ProjectAccessMixin, UserPassesTestMixin):
    """Solo OWNER."""

    def test_func(self) -> bool:
        return self.get_role() == ProjectMembership.Role.OWNER.value
