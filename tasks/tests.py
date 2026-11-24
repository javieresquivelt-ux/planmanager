import pytest
from django.contrib.auth import get_user_model

from projects.models import Project

from .models import Attachment, Comment, Task

User = get_user_model()


@pytest.mark.django_db
def test_task_comment_attachment_creation():
    user = User.objects.create_user(email="u@example.com", password="pass12345")
    project = Project.objects.create(name="P1", owner=user)
    task = Task.objects.create(
        project=project, title="T1", created_by=user, assignee=user
    )
    comment = Comment.objects.create(task=task, author=user, body="hola")
    attachment = Attachment.objects.create(
        task=task, uploaded_by=user, file="attachments/x.txt"
    )

    assert task.project == project
    assert task.status == Task.Status.TODO
    assert task.priority == Task.Priority.MEDIUM
    assert list(task.comments.all()) == [comment]
    assert list(task.attachments.all()) == [attachment]
