"""
URL configuration for planmanager project.
"""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

from core import views as core_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    path("", core_views.home, name="home"),
    path("dashboard/", core_views.DashboardView.as_view(), name="dashboard"),
    path("users/", include("users.urls")),
    path("projects/", include("projects.urls")),
    path("", include("tasks.urls")),
    # Servir media (uploads: avatares y adjuntos) tanto en desarrollo como en producción.
    # django.conf.urls.static.static() retorna [] cuando DEBUG=False, por lo que usamos
    # django.views.static.serve directamente con MEDIA_ROOT.
    re_path(
        r"^media/(?P<path>.*)$",
        serve,
        {"document_root": settings.MEDIA_ROOT, "show_indexes": False},
    ),
]
