from typing import Any

from django import forms

from .models import Project, ProjectMembership


class ProjectForm(forms.ModelForm[Project]):
    class Meta:
        model = Project
        fields = ["name", "description", "status"]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        if "status" in self.fields:
            self.fields["status"].required = False
            self.fields["status"].initial = Project.Status.OPEN

    def clean_status(self) -> str:
        status = self.cleaned_data.get("status")
        if not status:
            return Project.Status.OPEN.value
        return str(status)


class MemberAddForm(forms.Form):
    email = forms.EmailField()
    role = forms.ChoiceField(
        choices=ProjectMembership.Role.choices,
        initial=ProjectMembership.Role.MEMBER,
    )
