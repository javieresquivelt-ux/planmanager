from typing import Any, cast

from django import forms
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from projects import permissions
from projects.mixins import ProjectMemberRequiredMixin
from projects.models import ProjectMembership
from users.models import User

from . import selectors, services
from .forms import CommentForm, TaskForm
from .models import Task

_MANAGER_OR_ABOVE = {
    ProjectMembership.Role.MANAGER.value,
    ProjectMembership.Role.OWNER.value,
}


class TaskListView(ProjectMemberRequiredMixin, ListView[Task]):
    template_name = "tasks/list.html"
    context_object_name = "tasks"

    def get_queryset(self) -> QuerySet[Task]:
        return selectors.tasks_for_project(self.get_project())

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        project = self.get_project()
        ctx["project"] = project
        ctx["user_role"] = self.get_role()
        ctx["task_form"] = TaskForm(project=project, can_assign=self._can_assign())
        return ctx

    def _can_assign(self) -> bool:
        return self.get_role() in _MANAGER_OR_ABOVE


class TaskCreateView(ProjectMemberRequiredMixin, CreateView[Task]):
    model = Task
    form_class = TaskForm
    template_name = "tasks/form.html"

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["project"] = self.get_project()
        kwargs["can_assign"] = self.get_role() in _MANAGER_OR_ABOVE
        return kwargs

    def form_valid(self, form: forms.ModelForm[Task]) -> HttpResponse:
        if not permissions.can_create_task(self.get_role()):
            return HttpResponseForbidden()
        self.object = services.create_task(
            project=self.get_project(),
            created_by=cast(User, self.request.user),
            **form.cleaned_data,
        )
        return redirect(self.object.get_absolute_url())


class TaskDetailView(ProjectMemberRequiredMixin, DetailView[Task]):
    model = Task
    template_name = "tasks/detail.html"
    context_object_name = "task"

    def get_queryset(self) -> QuerySet[Task]:
        return Task.objects.filter(project=self.get_project()).select_related(
            "assignee", "project"
        )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        ctx["user_role"] = self.get_role()
        ctx["comments"] = selectors.comments_for_task(self.object)
        ctx["form"] = CommentForm()
        ctx["can_edit"] = permissions.can_edit_task(
            self.get_role(), self.object, cast(User, self.request.user)
        )
        ctx["can_comment"] = permissions.can_comment(self.get_role())
        return ctx


class TaskUpdateView(ProjectMemberRequiredMixin, UpdateView[Task]):
    model = Task
    form_class = TaskForm
    template_name = "tasks/form.html"

    def get_queryset(self) -> QuerySet[Task]:
        qs = Task.objects.filter(project=self.get_project())
        if self.get_role() in _MANAGER_OR_ABOVE:
            return qs
        return qs.filter(created_by=cast(User, self.request.user))

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["project"] = self.get_project()
        kwargs["can_assign"] = self.get_role() in _MANAGER_OR_ABOVE
        return kwargs


class TaskDeleteView(ProjectMemberRequiredMixin, DeleteView[Task]):
    model = Task
    template_name = "tasks/confirm_delete.html"

    def get_queryset(self) -> QuerySet[Task]:
        qs = Task.objects.filter(project=self.get_project())
        if self.get_role() in _MANAGER_OR_ABOVE:
            return qs
        return qs.filter(created_by=cast(User, self.request.user))

    def get_success_url(self) -> str:
        return reverse(
            "tasks:list", kwargs={"project_pk": self.get_project().pk}
        )


class TaskStatusView(ProjectMemberRequiredMixin, View):
    def post(self, request: HttpRequest, project_pk: int, pk: int) -> HttpResponse:
        task = get_object_or_404(Task, pk=pk, project=self.get_project())
        role = self.get_role()
        user = cast(User, request.user)
        if not permissions.can_edit_task(role, task, user):
            return HttpResponseForbidden()
        status = request.POST.get("status")
        if status is not None and status in Task.Status.values:
            task = services.change_task_status(task, status)
        context = {
            "task": task,
            "can_edit": permissions.can_edit_task(role, task, user),
        }
        if request.headers.get("HX-Request"):
            return render(request, "tasks/partials/task_status.html", context)
        return redirect("tasks:detail", project_pk=task.project_id, pk=task.pk)


class CommentCreateView(ProjectMemberRequiredMixin, View):
    def post(self, request: HttpRequest, project_pk: int, pk: int) -> HttpResponse:
        task = get_object_or_404(Task, pk=pk, project=self.get_project())
        role = self.get_role()
        if not permissions.can_comment(role):
            return HttpResponseForbidden()
        form = CommentForm(request.POST)
        if form.is_valid():
            services.add_comment(task, cast(User, request.user), form.cleaned_data["body"])
        context = {
            "task": task,
            "can_comment": permissions.can_comment(role),
            "comments": selectors.comments_for_task(task),
            "form": CommentForm(),
        }
        if request.headers.get("HX-Request"):
            return render(request, "tasks/partials/comments.html", context)
        return redirect("tasks:detail", project_pk=task.project_id, pk=task.pk)
