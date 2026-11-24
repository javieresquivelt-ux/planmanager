import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import RequestFactory
from django.urls import reverse

from tasks.models import Task

from . import permissions
from .mixins import (
    ProjectManagerRequiredMixin,
    ProjectMemberRequiredMixin,
    ProjectOwnerRequiredMixin,
)
from .models import Project, ProjectMembership

User = get_user_model()


@pytest.mark.django_db
def test_get_role_returns_role():
    user = User.objects.create_user(email="u@example.com", password="pass12345")
    project = Project.objects.create(name="P1", owner=user)
    ProjectMembership.objects.create(
        project=project, user=user, role=ProjectMembership.Role.MANAGER
    )
    assert ProjectMembership.get_role(user, project) == "MANAGER"


@pytest.mark.django_db
def test_get_role_none_when_not_member():
    user = User.objects.create_user(email="u@example.com", password="pass12345")
    other = User.objects.create_user(email="o@example.com", password="pass12345")
    project = Project.objects.create(name="P1", owner=user)
    assert ProjectMembership.get_role(other, project) is None


@pytest.mark.django_db
def test_membership_unique_together():
    user = User.objects.create_user(email="u@example.com", password="pass12345")
    project = Project.objects.create(name="P1", owner=user)
    ProjectMembership.objects.create(project=project, user=user, role="MEMBER")
    with pytest.raises(IntegrityError):
        ProjectMembership.objects.create(project=project, user=user, role="VIEWER")


@pytest.mark.django_db
def test_members_m2m_through():
    user = User.objects.create_user(email="u@example.com", password="pass12345")
    project = Project.objects.create(name="P1", owner=user)
    ProjectMembership.objects.create(project=project, user=user, role="MEMBER")
    assert list(project.members.all()) == [user]
    assert list(user.projects.all()) == [project]


def _membership_scenario():
    owner = User.objects.create_user(email="owner@example.com", password="pass12345")
    manager = User.objects.create_user(email="manager@example.com", password="pass12345")
    member = User.objects.create_user(email="member@example.com", password="pass12345")
    viewer = User.objects.create_user(email="viewer@example.com", password="pass12345")
    outsider = User.objects.create_user(email="outsider@example.com", password="pass12345")
    project = Project.objects.create(name="Proyecto Alpha", owner=owner)
    ProjectMembership.objects.create(project=project, user=owner, role="OWNER")
    ProjectMembership.objects.create(project=project, user=manager, role="MANAGER")
    ProjectMembership.objects.create(project=project, user=member, role="MEMBER")
    ProjectMembership.objects.create(project=project, user=viewer, role="VIEWER")
    return owner, manager, member, viewer, outsider, project


@pytest.fixture
def rf():
    return RequestFactory()


@pytest.mark.django_db
def test_project_access_mixins(rf):
    owner, manager, member, viewer, outsider, project = _membership_scenario()

    def test_func(view_cls, user):
        view = view_cls()
        view.request = rf.get("/")
        view.request.user = user
        view.kwargs = {"project_pk": project.pk}
        return view.test_func()

    assert test_func(ProjectMemberRequiredMixin, owner) is True
    assert test_func(ProjectMemberRequiredMixin, manager) is True
    assert test_func(ProjectMemberRequiredMixin, member) is True
    assert test_func(ProjectMemberRequiredMixin, viewer) is True
    assert test_func(ProjectMemberRequiredMixin, outsider) is False

    assert test_func(ProjectManagerRequiredMixin, owner) is True
    assert test_func(ProjectManagerRequiredMixin, manager) is True
    assert test_func(ProjectManagerRequiredMixin, member) is False
    assert test_func(ProjectManagerRequiredMixin, viewer) is False

    assert test_func(ProjectOwnerRequiredMixin, owner) is True
    assert test_func(ProjectOwnerRequiredMixin, manager) is False


@pytest.mark.django_db
def test_permission_matrix():
    owner, manager, member, viewer, outsider, project = _membership_scenario()
    own_task = Task.objects.create(project=project, title="own", created_by=member)
    other_task = Task.objects.create(project=project, title="other", created_by=manager)

    assert permissions.can_view("VIEWER") is True
    assert permissions.can_view(None) is False

    assert permissions.can_create_task("MEMBER") is True
    assert permissions.can_create_task("VIEWER") is False

    assert permissions.can_edit_task("MEMBER", own_task, member) is True
    assert permissions.can_edit_task("MEMBER", other_task, member) is False
    assert permissions.can_edit_task("MANAGER", other_task, manager) is True

    assert permissions.can_assign_task("MANAGER") is True
    assert permissions.can_assign_task("MEMBER") is False

    assert permissions.can_comment("MEMBER") is True
    assert permissions.can_comment("VIEWER") is False

    assert permissions.can_manage_members("OWNER") is True
    assert permissions.can_manage_members("MANAGER") is False

    assert permissions.can_edit_project("OWNER") is True
    assert permissions.can_edit_project("MANAGER") is False


@pytest.mark.django_db
def test_project_list_only_member_projects(client):
    owner, manager, member, viewer, outsider, project = _membership_scenario()
    client.force_login(owner)
    resp = client.get(reverse("projects:list"))
    assert resp.status_code == 200
    assert project.name.encode() in resp.content

    client.force_login(outsider)
    resp = client.get(reverse("projects:list"))
    assert project.name.encode() not in resp.content


@pytest.mark.django_db
def test_project_create_creates_owner_membership(client):
    user = User.objects.create_user(email="new@example.com", password="pass12345")
    client.force_login(user)
    resp = client.post(
        reverse("projects:create"), {"name": "Nuevo", "description": "d"}
    )
    assert resp.status_code == 302
    project = Project.objects.get(name="Nuevo")
    assert project.owner == user
    assert ProjectMembership.get_role(user, project) == "OWNER"


@pytest.mark.django_db
def test_project_detail_outsider_forbidden(client):
    owner, manager, member, viewer, outsider, project = _membership_scenario()
    client.force_login(outsider)
    resp = client.get(reverse("projects:detail", kwargs={"project_pk": project.pk}))
    assert resp.status_code == 403


@pytest.mark.django_db
def test_member_add_owner_only(client):
    owner, manager, member, viewer, outsider, project = _membership_scenario()

    client.force_login(manager)
    resp = client.post(
        reverse("projects:member_add", kwargs={"project_pk": project.pk}),
        {"email": "x@example.com", "role": "MEMBER"},
    )
    assert resp.status_code == 403

    User.objects.create_user(email="added@example.com", password="pass12345")
    client.force_login(owner)
    resp = client.post(
        reverse("projects:member_add", kwargs={"project_pk": project.pk}),
        {"email": "added@example.com", "role": "MEMBER"},
    )
    assert resp.status_code == 302
    added = User.objects.get(email="added@example.com")
    assert ProjectMembership.get_role(added, project) == "MEMBER"
