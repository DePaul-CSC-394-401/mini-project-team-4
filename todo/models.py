from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
    
# Team model: represents the team in the application
class Team(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    members = models.ManyToManyField(User, related_name='teams') # many users can be part of same team & users can belong to >1 team

    def __str__(self):
        return self.name

# Todo model
class Todo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True)
    assigned_users = models.ManyToManyField(User, related_name="assigned_tasks", blank=True)

    PRIORITY_CHOICES = [('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High'),]

    title = models.CharField(max_length=100)
    details = models.TextField()
    date = models.DateTimeField(default=timezone.now)
    completed = models.BooleanField(default=False)
    priority = models.CharField(max_length=6, choices=PRIORITY_CHOICES, default='Medium')
    #team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True) # opional field

    def __str__(self):
        return self.title

class TodoTimer(models.Model):
    todo = models.ForeignKey(Todo, on_delete=models.CASCADE, related_name='timers')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    
    def total_time(self):
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds() / 60  # Total time in minutes
        return 0