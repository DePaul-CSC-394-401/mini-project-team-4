from django.core.management.base import BaseCommand
from todo.tasks import check_due_dates_and_send_reminders  # Import your reminder function

class Command(BaseCommand):  # Make sure the class is named "Command"
    help = 'Check for upcoming task reminders and send them via email.'

    def handle(self, *args, **kwargs):
        check_due_dates_and_send_reminders()  # Call the reminder function
