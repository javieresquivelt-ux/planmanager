from django import forms

from .models import Project, ProjectMembership


class ProjectForm(forms.ModelForm[Project]):
    class Meta:
        model = Project
        fields = ["name", "description"]


class MemberAddForm(forms.Form):
    email = forms.EmailField()
    role = forms.ChoiceField(
        choices=ProjectMembership.Role.choices,
        initial=ProjectMembership.Role.MEMBER,
    )
