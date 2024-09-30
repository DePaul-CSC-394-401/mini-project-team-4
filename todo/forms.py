from django import forms
from .models import Todo


class TodoForm(forms.ModelForm):
    class Meta:
        model = Todo
        fields = ['title', 'details', 'date', 'priority', 'due_date', 'reminder_time', 'category']
        widgets = {
            'dude_date':forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }