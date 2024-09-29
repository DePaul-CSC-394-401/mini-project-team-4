from django import forms
from .models import Team, Todo
from django.contrib.auth.models import User

class TodoForm(forms.ModelForm):
    assigned_users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Todo
        fields = ['title', 'details', 'date', 'priority', 'team', 'assigned_users']

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'description', 'members']
