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
    
    # dynamic updating of the teams in query
    def __init__(self, *args, **kwargs):
        # Use the current user to filter teams in the form
        user = kwargs.pop('user', None)
        super(TodoForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['team'].queryset = Team.objects.filter(members=user)

class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'description', 'members']
