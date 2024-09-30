from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta

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
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Other')
    due_date = models.DateTimeField(default=timezone.now)
    reminder_time=models.DurationField(null=True, blank=True,
        help_text="Time before the due date when the reminder should be sent (e.g., 1 day or 1 hour)."
    )
    reminder_sent = models.BooleanField(default=False)
    
    def __str__(self):
        return self.title
    