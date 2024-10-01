from django.utils.timezone import now
from .models import Todo
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def check_due_dates_and_send_reminders():
    """
    This function checks all tasks that have a due date set, haven't had a reminder sent,
    and sends a reminder if the current time is within the reminder window.
    """
    # Get all tasks that haven't had a reminder sent and have a due date set
    todos = Todo.objects.filter(remind_sent=False, due_date__isnull=False)

    for todo in todos:
        # Calculate the time remaining until the due date
        time_until_due = todo.due_date - now()

        # Check if the current time is within the reminder window (reminder_time)
        if todo.reminder_time and time_until_due <= todo.reminder_time:
            send_reminder(todo)  # Send the reminder
            todo.reminder_sent = True  # Mark the reminder as sent
            todo.save()  # Save the updated task


def send_reminder(todo):
    """
    This function sends a reminder email to the user for a task that is due soon.
    """
    subject = f"Reminder: {todo.title} is due soon!"

    html_message = render_to_string('todo/reminder_email.html', {'todo': todo, 'user': todo.user})
    plain_message = strip_tags(html_message)  
    recipient = todo.user.email  

    send_mail(
        subject,
        plain_message,  
        settings.EMAIL_HOST_USER,  
        [recipient],  # To email
        html_message=html_message  # Rendered HTML message
    )
