from django.contrib.auth.decorators import login_required
from django.views.generic.edit import FormView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import TodoForm
from django.db.models import Q
from .models import Todo
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django import forms
from django.contrib.auth.models import User
from django.utils import timezone

from django.core.mail import send_mail
from django.conf import settings  # for accessing email config
from django.template.loader import render_to_string
from django.utils.html import strip_tags


class CustomLoginView(LoginView):
    template_name = 'todo/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('todo')


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ['email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['email']  # Set the username to the email
        if commit:
            user.save()
        return user
    

class RegisterPage(FormView):
    template_name = 'todo/register.html'
    form_class = CustomUserCreationForm  
    redirect_authenticated_user = True
    success_url = reverse_lazy('todo')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
            subject = 'Registration Successful - Email Confirmation'
            html_message = render_to_string('todo/email_confirmation.html', {'user': user})
            plain_message = strip_tags(html_message)  
            send_mail(subject, plain_message, settings.EMAIL_HOST_USER, [user.email], html_message=html_message)

        return super(RegisterPage, self).form_valid(form)


@login_required
def index(request):
    # Get the search query and sort option from the request
    query = request.GET.get('q', None)
    sort_by = request.GET.get('sort_by', None)
    category_filter = request.GET.get('category', None)

    # Filter todos by the logged-in user
    item_list = Todo.objects.filter(user=request.user, archived=False)

    if category_filter:
        item_list = item_list.filter(category=category_filter)

    now = timezone.now()
    for item in item_list:
        if item.reminder_time and not item.reminder_sent:
            reminder_due_time = item.due_date - item.reminder_time
            if now >= reminder_due_time:
                item.reminder_sent = True
                item.save()
                messages.info(request, f'Reminder: Task "{item.title}" is due soon!')

    if query:
        # Filter items by title or description (details) if a search query exists
        item_list = item_list.filter(Q(title__icontains=query) | Q(details__icontains=query))

    # Apply sorting based on the selected option
    if sort_by == 'priority':
        # Sort by priority: highest ('High') to lowest ('Low')
        priority_order = {'High': 1, 'Medium': 2, 'Low': 3}
        item_list = sorted(item_list, key=lambda x: priority_order[x.priority])
    elif sort_by == 'date':
        # Sort by date: nearest to farthest due date
        item_list = item_list.order_by('date')
    else:
        # Default sorting by creation date descending
        item_list = item_list.order_by('-date')

    form = TodoForm(request.POST or None)
    if request.method == "POST":
        form = TodoForm(request.POST)
        if form.is_valid():
            todo_item = form.save(commit=False)
            todo_item.user = request.user
            todo_item.save()
            return redirect('todo')
    else:
        form = TodoForm()

    page = {
        "forms": form,
        "list": item_list,
        "title": "TODO LIST",
        "Current_category" : category_filter
    }
    return render(request, 'todo/index.html', page)

def archive_task(request, task_id):
    task = get_object_or_404(Todo, id=task_id, user=request.user)
    task.archived = True
    task.save()
    messages.success(request, f'Task "{task.title}" archived successfully!')
    return redirect('todo')

def view_archive(request):
    archived_task = Todo.objects.filter(user=request.user, archived=True).order_by('-date')

    page = {
        "list": archived_task,
        "title": "archived TODO Items",
    }
    return render(request,'todo/archive.html', page )


@login_required
def remove(request, item_id):
    item = get_object_or_404(Todo, id=item_id, user=request.user)

    if request.method == "POST":
        item.delete()
        messages.info(request, "Item removed!")
        return redirect('todo')
    
    return render(request, 'todo/confirm_delete.html', {'item': item})


@login_required
def edit(request, item_id):
    item = get_object_or_404(Todo, id=item_id, user=request.user)
    if request.method == "POST":
        form = TodoForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, "Item updated successfully!")
            return redirect('todo')
    else:
        form = TodoForm(instance=item)

    page = {
        "forms": form,
        "title": "Edit TODO Item",
        "item_id": item_id,
    }
    return render(request, 'todo/edit.html', page)

@login_required
def mark_complete(request, item_id):
    item = get_object_or_404(Todo, id=item_id, user=request.user)
    item.completed = True
    item.save()
    return redirect('todo')


@login_required
def update_email(request):
    if request.method == 'POST':
        new_email = request.POST.get('email')

        # Check if the new email is different from the current email
        if new_email != request.user.email:
            user = request.user
            # Update both email and username fields
            user.email = new_email
            user.username = new_email  # Assuming you are using email as the username
            user.save(update_fields=['email', 'username'])  # Update both fields

            # Log the user in again to refresh the session with the new email/username
            login(request, user)

            messages.success(request, 'Email updated successfully!')
        else:
            messages.info(request, 'New email is the same as the current email.')

        return redirect('todo')


@login_required
def change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        new_password2 = request.POST.get('new_password2')

        if new_password != new_password2:
            messages.error(request, "New passwords do not match.")
            return redirect('profile')  # Redirect back to profile

        user = request.user
        if user.check_password(old_password):
            user.set_password(new_password)
            user.save()
            messages.success(request, "Password changed successfully!")
            return redirect('login')  # Re-login after password change
        else:
            messages.error(request, "Old password is incorrect.")
            return redirect('profile')