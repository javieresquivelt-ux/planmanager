import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from projects.models import Project, ProjectMembership
from tasks.models import Task

User = get_user_model()


@pytest.mark.django_db
def test_dashboard_requires_login(client):
    resp = client.get(reverse("dashboard"))
    assert resp.status_code == 302
    assert resp.url.startswith(reverse("users:login"))


@pytest.mark.django_db
def test_dashboard_metrics(client):
    user = User.objects.create_user(email="u@example.com", password="pass12345")
    project = Project.objects.create(name="P1", owner=user)
    ProjectMembership.objects.create(project=project, user=user, role="OWNER")
    Task.objects.create(project=project, title="A", created_by=user, status="DONE")
    Task.objects.create(project=project, title="B", created_by=user, status="TODO")

    client.force_login(user)
    resp = client.get(reverse("dashboard"))
    assert resp.status_code == 200
    content = resp.content.decode()
    assert "P1" in content
    assert "Propietario" in content
    assert "2" in content  # total tareas
    assert "1" in content  # completadas


@pytest.mark.django_db
def test_dashboard_only_own_projects(client):
    user = User.objects.create_user(email="u@example.com", password="pass12345")
    other = User.objects.create_user(email="o@example.com", password="pass12345")
    own = Project.objects.create(name="Propio", owner=user)
    ProjectMembership.objects.create(project=own, user=user, role="OWNER")
    Project.objects.create(name="Ajeno", owner=other)

    client.force_login(user)
    resp = client.get(reverse("dashboard"))
    content = resp.content.decode()
    assert "Propio" in content
    assert "Ajeno" not in content
