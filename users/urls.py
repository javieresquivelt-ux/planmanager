from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import UserLoginForm

app_name = "users"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path(
        "login/",
        auth_views.LoginView.as_view(
            form_class=UserLoginForm,
            template_name="registration/login.html",
        ),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("manage/", views.UserManagementView.as_view(), name="manage"),
    path("<int:user_pk>/role/", views.UserRoleUpdateView.as_view(), name="update_role"),
]
