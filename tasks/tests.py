import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from projects.models import Project, ProjectMembership

from .models import Attachment, Comment, Task

User = get_user_model()


@pytest.mark.django_db
def test_task_comment_attachment_creation():
    user = User.objects.create_user(email="u@example.com", password="pass12345")
    project = Project.objects.create(name="P1", owner=user)
    task = Task.objects.create(
        project=project, title="T1", created_by=user
    )
    task.assignees.add(user)
    comment = Comment.objects.create(task=task, author=user, body="hola")
    attachment = Attachment.objects.create(
        task=task, uploaded_by=user, file="attachments/x.txt"
    )

    assert task.project == project
    assert task.status == Task.Status.TODO
    assert task.priority == Task.Priority.MEDIUM
    assert list(task.comments.all()) == [comment]
    assert list(task.attachments.all()) == [attachment]


@pytest.mark.django_db
def test_task_multiple_assignees(client):
    owner = User.objects.create_user(email="owner@example.com", password="pass12345")
    member1 = User.objects.create_user(email="m1@example.com", password="pass12345")
    member2 = User.objects.create_user(email="m2@example.com", password="pass12345")
    project = Project.objects.create(name="P", owner=owner)
    ProjectMembership.objects.create(project=project, user=owner, role="OWNER")
    ProjectMembership.objects.create(project=project, user=member1, role="MEMBER")
    ProjectMembership.objects.create(project=project, user=member2, role="MEMBER")

    client.force_login(owner)
    resp = client.post(
        reverse("tasks:create", kwargs={"project_pk": project.pk}),
        {
            "title": "Tarea multi",
            "status": "TODO",
            "priority": "MEDIUM",
            "due_date": "",
            "assignees": [member1.id, member2.id],
        },
    )
    assert resp.status_code == 302
    task = Task.objects.get(title="Tarea multi")
    assert set(task.assignees.all()) == {member1, member2}


def _task_scenario():
    owner = User.objects.create_user(email="owner@example.com", password="pass12345")
    manager = User.objects.create_user(email="manager@example.com", password="pass12345")
    member = User.objects.create_user(email="member@example.com", password="pass12345")
    viewer = User.objects.create_user(email="viewer@example.com", password="pass12345")
    project = Project.objects.create(name="P", owner=owner)
    ProjectMembership.objects.create(project=project, user=owner, role="OWNER")
    ProjectMembership.objects.create(project=project, user=manager, role="MANAGER")
    ProjectMembership.objects.create(project=project, user=member, role="MEMBER")
    ProjectMembership.objects.create(project=project, user=viewer, role="VIEWER")
    task = Task.objects.create(project=project, title="T", created_by=member)
    return owner, manager, member, viewer, project, task


@pytest.mark.django_db
def test_task_create_by_member(client):
    owner, manager, member, viewer, project, task = _task_scenario()
    client.force_login(member)
    resp = client.post(
        reverse("tasks:create", kwargs={"project_pk": project.pk}),
        {"title": "Nueva tarea", "status": "TODO", "priority": "MEDIUM", "due_date": ""},
    )
    assert resp.status_code == 302
    assert Task.objects.filter(title="Nueva tarea").exists()


@pytest.mark.django_db
def test_task_detail_viewer_can_view_but_not_edit(client):
    owner, manager, member, viewer, project, task = _task_scenario()
    url = reverse("tasks:detail", kwargs={"project_pk": project.pk, "pk": task.pk})
    client.force_login(viewer)
    resp = client.get(url)
    assert resp.status_code == 200
    assert b"Editar" not in resp.content


@pytest.mark.django_db
def test_status_change_member_own_task(client):
    owner, manager, member, viewer, project, task = _task_scenario()
    client.force_login(member)
    resp = client.post(
        reverse("tasks:status", kwargs={"project_pk": project.pk, "pk": task.pk}),
        {"status": "DONE"},
    )
    assert resp.status_code == 302
    task.refresh_from_db()
    assert task.status == "DONE"


@pytest.mark.django_db
def test_status_change_member_not_own_forbidden(client):
    owner, manager, member, viewer, project, task = _task_scenario()
    other = Task.objects.create(project=project, title="O", created_by=manager)
    client.force_login(member)
    resp = client.post(
        reverse("tasks:status", kwargs={"project_pk": project.pk, "pk": other.pk}),
        {"status": "DONE"},
    )
    assert resp.status_code == 403



@pytest.mark.django_db
def test_add_comment_htmx_partial(client):
    owner, manager, member, viewer, project, task = _task_scenario()
    client.force_login(member)
    url = reverse("tasks:comment", kwargs={"project_pk": project.pk, "pk": task.pk})
    resp = client.post(url, {"body": "hola"}, HTTP_HX_REQUEST="true")
    assert resp.status_code == 200
    assert task.comments.count() == 1
    assert b"hola" in resp.content


@pytest.mark.django_db
def test_add_comment_viewer_forbidden(client):
    owner, manager, member, viewer, project, task = _task_scenario()
    client.force_login(viewer)
    url = reverse("tasks:comment", kwargs={"project_pk": project.pk, "pk": task.pk})
    resp = client.post(url, {"body": "hola"})
    assert resp.status_code == 403


@pytest.mark.django_db
def test_task_list_displays_dates(client):
    import datetime
    owner, manager, member, viewer, project, task = _task_scenario()
    task.due_date = datetime.date(2026, 12, 31)
    task.save()

    client.force_login(member)
    resp = client.get(reverse("tasks:list", kwargs={"project_pk": project.pk}))
    assert resp.status_code == 200
    content = resp.content.decode()
    assert "Creada:" in content or "Created:" in content
    assert "Límite:" in content or "Due:" in content
    assert "2026" in content


@pytest.mark.django_db
def test_task_list_kanban_columns_and_views(client):
    owner, manager, member, viewer, project, task1 = _task_scenario()
    task2 = Task.objects.create(
        project=project,
        title="Task In Progress",
        status=Task.Status.IN_PROGRESS,
        created_by=owner,
    )
    task3 = Task.objects.create(
        project=project,
        title="Task Done",
        status=Task.Status.DONE,
        created_by=owner,
    )

    client.force_login(owner)
    url = reverse("tasks:list", kwargs={"project_pk": project.pk})
    resp = client.get(url)
    assert resp.status_code == 200

    cols = resp.context["kanban_columns"]
    assert len(cols) == 4
    todo_col = next(c for c in cols if c["status"] == "TODO")
    in_prog_col = next(c for c in cols if c["status"] == "IN_PROGRESS")
    done_col = next(c for c in cols if c["status"] == "DONE")

    assert task1 in todo_col["tasks"]
    assert task2 in in_prog_col["tasks"]
    assert task3 in done_col["tasks"]

    content = resp.content.decode()
    assert "Kanban" in content
    assert "Lista" in content
    assert "Task In Progress" in content
    assert "Task Done" in content


@pytest.mark.django_db
def test_task_status_update_with_next_url(client):
    owner, manager, member, viewer, project, task = _task_scenario()
    client.force_login(owner)
    status_url = reverse(
        "tasks:status", kwargs={"project_pk": project.pk, "pk": task.pk}
    )
    list_url = reverse("tasks:list", kwargs={"project_pk": project.pk})

    resp = client.post(
        status_url,
        {"status": "IN_PROGRESS", "next": list_url},
    )
    assert resp.status_code == 302
    assert resp.url == list_url
    task.refresh_from_db()
    assert task.status == Task.Status.IN_PROGRESS


@pytest.mark.django_db
def test_comment_edit_and_delete(client):
    owner, manager, member, viewer, project, task = _task_scenario()
    comment = Comment.objects.create(task=task, author=member, body="Comentario original")

    # Autor (member) puede editar su comentario
    client.force_login(member)
    edit_url = reverse(
        "tasks:comment_update",
        kwargs={"project_pk": project.pk, "pk": task.pk, "comment_pk": comment.pk},
    )
    resp = client.post(edit_url, {"body": "Comentario editado"}, HTTP_HX_REQUEST="true")
    assert resp.status_code == 200
    comment.refresh_from_db()
    assert comment.body == "Comentario editado"

    # Otro usuario (viewer u otro member) no puede editar
    client.force_login(viewer)
    resp = client.post(edit_url, {"body": "Hack"})
    assert resp.status_code == 403

    # Otro usuario ordinario no puede eliminar el comentario de otro
    delete_url = reverse(
        "tasks:comment_delete",
        kwargs={"project_pk": project.pk, "pk": task.pk, "comment_pk": comment.pk},
    )
    resp = client.post(delete_url)
    assert resp.status_code == 403

    # Manager / JP SÍ puede moderar y eliminar el comentario
    client.force_login(manager)
    resp = client.post(delete_url, HTTP_HX_REQUEST="true")
    assert resp.status_code == 200
    assert not Comment.objects.filter(pk=comment.pk).exists()

