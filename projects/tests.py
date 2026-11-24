import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

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
