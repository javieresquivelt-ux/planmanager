"""
URL configuration for planmanager project.
"""

from django.contrib import admin
from django.urls import include, path

from core import views as core_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    path("", core_views.home, name="home"),
    path("users/", include("users.urls")),
    path("projects/", include("projects.urls")),
    path("", include("tasks.urls")),
]
