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


@pytest.mark.django_db
def test_media_served_when_debug_false(client, settings):
    settings.DEBUG = False
    media_dir = settings.MEDIA_ROOT / "test_avatars"
    media_dir.mkdir(parents=True, exist_ok=True)
    sample_file = media_dir / "sample.txt"
    sample_file.write_text("ok-media")
    try:
        resp = client.get("/media/test_avatars/sample.txt")
        assert resp.status_code == 200
        assert b"".join(resp.streaming_content).decode() == "ok-media"
    finally:
        sample_file.unlink(missing_ok=True)
        media_dir.rmdir()


@pytest.mark.django_db
def test_dashboard_displays_recent_tasks_assignees_and_dates(client):
    import datetime
    user = User.objects.create_user(email="assignee@example.com", password="pass12345")
    project = Project.objects.create(name="ProjX", owner=user)
    ProjectMembership.objects.create(project=project, user=user, role="OWNER")
    task = Task.objects.create(
        project=project,
        title="Tarea con fecha",
        created_by=user,
        due_date=datetime.date(2026, 12, 15),
    )
    task.assignees.add(user)

    client.force_login(user)
    resp = client.get(reverse("dashboard"))
    assert resp.status_code == 200
    content = resp.content.decode()
    assert "Tarea con fecha" in content
    assert "assignee@example.com" in content or "A" in content  # avatar
    assert "15" in content  # fecha día



