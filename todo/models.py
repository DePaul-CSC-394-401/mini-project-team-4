from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
<<<<<<< HEAD
from datetime import timedelta
=======
    
# Team model: represents the team in the application
class Team(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    members = models.ManyToManyField(User, related_name='teams') # many users can be part of same team & users can belong to >1 team
>>>>>>> e29c6a52f58f89f7f853a9fde1b0ca5b1e681b21

    def __str__(self):
        return self.name

# Todo model
class Todo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)

    PRIORITY_CHOICES = [('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High'),]
    CATEGORY_CHOICES = [ ('Work', 'Work'),
        ('Personal', 'Personal'),
        ('Errands', 'Errands'),
        ('Other', 'Other'),
        ]

    title = models.CharField(max_length=100)
    details = models.TextField()
    date = models.DateTimeField(default=timezone.now)
    archived = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    priority = models.CharField(max_length=6, choices=PRIORITY_CHOICES, default='Medium')
<<<<<<< HEAD
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Other')
    due_date = models.DateTimeField(default=timezone.now)
    reminder_time=models.DurationField(null=True, blank=True,
        help_text="Time before the due date when the reminder should be sent (e.g., 1 day or 1 hour)."
    )
    reminder_sent = models.BooleanField(default=False)
    
=======
    #team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True) # opional field

>>>>>>> e29c6a52f58f89f7f853a9fde1b0ca5b1e681b21
    def __str__(self):
        return self.title

    