from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404

from .models import Project, ProjectMembership


class ProjectAccessMixin:
    """Resuelve el proyecto actual y cachea el rol del usuario por request."""

    project_kwarg = "project_pk"

    def get_project(self):
        if not hasattr(self, "_project"):
            self._project = get_object_or_404(
                Project, pk=self.kwargs[self.project_kwarg]
            )
        return self._project

    def get_role(self):
        if not hasattr(self, "_role"):
            self._role = ProjectMembership.get_role(
                self.request.user, self.get_project()
            )
        return self._role


class ProjectMemberRequiredMixin(ProjectAccessMixin, UserPassesTestMixin):
    """Cualquier miembro del proyecto (VIEWER o superior)."""

    def test_func(self):
        return self.get_role() is not None


class ProjectManagerRequiredMixin(ProjectAccessMixin, UserPassesTestMixin):
    """MANAGER u OWNER."""

    def test_func(self):
        return self.get_role() in {
            ProjectMembership.Role.MANAGER.value,
            ProjectMembership.Role.OWNER.value,
        }


class ProjectOwnerRequiredMixin(ProjectAccessMixin, UserPassesTestMixin):
    """Solo OWNER."""

    def test_func(self):
        return self.get_role() == ProjectMembership.Role.OWNER.value
