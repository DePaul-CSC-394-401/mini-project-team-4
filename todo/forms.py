from django import forms
from .models import Team, Todo


class TodoForm(forms.ModelForm):
    class Meta:
        model = Todo
        fields = ['title', 'details', 'date', 'priority', 'due_date', 'reminder_time', 'category']
        widgets = {
            'dude_date':forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
        fields = ['title', 'details', 'date', 'priority']

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'description', 'members']
