from django import forms

from .models import Comment, Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "assignee", "status", "priority", "due_date"]
        widgets = {"due_date": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, *args, project=None, can_assign=True, **kwargs):
        super().__init__(*args, **kwargs)
        if project is not None:
            self.fields["assignee"].queryset = project.members.all()
        if not can_assign:
            self.fields.pop("assignee", None)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body"]
        widgets = {"body": forms.Textarea(attrs={"rows": 2})}
