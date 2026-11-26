from django.urls import path

from . import views

app_name = "projects"

urlpatterns = [
    path("", views.ProjectListView.as_view(), name="list"),
    path("export/csv/", views.ProjectPortfolioCSVView.as_view(), name="export_csv"),
    path("new/", views.ProjectCreateView.as_view(), name="create"),
    path("<int:project_pk>/", views.ProjectDetailView.as_view(), name="detail"),
    path("<int:project_pk>/status/", views.ProjectStatusView.as_view(), name="status"),
    path("<int:project_pk>/edit/", views.ProjectUpdateView.as_view(), name="update"),
    path(
        "<int:project_pk>/delete/",
        views.ProjectDeleteView.as_view(),
        name="delete",
    ),
    path(
        "<int:project_pk>/members/add/",
        views.MemberAddView.as_view(),
        name="member_add",
    ),
    path(
        "<int:project_pk>/members/<int:membership_pk>/role/",
        views.MemberRoleView.as_view(),
        name="member_role",
    ),
    path(
        "<int:project_pk>/members/<int:membership_pk>/remove/",
        views.MemberRemoveView.as_view(),
        name="member_remove",
    ),
]
