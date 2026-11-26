from django.urls import path

from . import views

app_name = "tasks"

urlpatterns = [
    path("<int:project_pk>/tasks/", views.TaskListView.as_view(), name="list"),
    path(
        "<int:project_pk>/tasks/new/",
        views.TaskCreateView.as_view(),
        name="create",
    ),
    path(
        "<int:project_pk>/tasks/<int:pk>/",
        views.TaskDetailView.as_view(),
        name="detail",
    ),
    path(
        "<int:project_pk>/tasks/<int:pk>/edit/",
        views.TaskUpdateView.as_view(),
        name="update",
    ),
    path(
        "<int:project_pk>/tasks/<int:pk>/delete/",
        views.TaskDeleteView.as_view(),
        name="delete",
    ),
    path(
        "<int:project_pk>/tasks/<int:pk>/status/",
        views.TaskStatusView.as_view(),
        name="status",
    ),
    path(
        "<int:project_pk>/tasks/<int:pk>/comment/",
        views.CommentCreateView.as_view(),
        name="comment",
    ),
    path(
        "<int:project_pk>/tasks/<int:pk>/comment/<int:comment_pk>/edit/",
        views.CommentUpdateView.as_view(),
        name="comment_update",
    ),
    path(
        "<int:project_pk>/tasks/<int:pk>/comment/<int:comment_pk>/delete/",
        views.CommentDeleteView.as_view(),
        name="comment_delete",
    ),
]
