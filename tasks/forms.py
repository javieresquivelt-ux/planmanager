from typing import Any

from django import forms

from projects.models import Project

from .models import Comment, Task


class TaskForm(forms.ModelForm[Task]):
    class Meta:
        model = Task
        fields = ["title", "description", "assignees", "status", "priority", "due_date"]
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}),
            "assignees": forms.CheckboxSelectMultiple,
        }

    def __init__(
        self,
        *args: Any,
        project: Project | None = None,
        can_assign: bool = True,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        if project is not None:
            assignees = self.fields.get("assignees")
            if isinstance(assignees, forms.ModelMultipleChoiceField):
                assignees.queryset = project.members.all()
        if not can_assign:
            self.fields.pop("assignees", None)


class CommentForm(forms.ModelForm[Comment]):
    class Meta:
        model = Comment
        fields = ["body"]
        widgets = {"body": forms.Textarea(attrs={"rows": 2})}
