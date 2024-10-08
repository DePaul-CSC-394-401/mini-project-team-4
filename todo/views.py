from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.generic.edit import FormView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import TeamForm, TodoForm
from django.db.models import Q
from .models import Team, Todo
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django import forms
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings  # for accessing email config
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.models import User
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from .models import Todo, TodoTimer


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
def start_timer(request, item_id):
    todo = get_object_or_404(Todo, id=item_id)
    # Start a new timer for the user if there is no ongoing timer
    if not TodoTimer.objects.filter(todo=todo, user=request.user, end_time__isnull=True).exists():
        TodoTimer.objects.create(todo=todo, user=request.user, start_time=timezone.now())
    return redirect('todo')

@login_required
def stop_timer(request, item_id):
    todo = get_object_or_404(Todo, id=item_id)
    # Stop the most recent timer if it is running
    timer = TodoTimer.objects.filter(todo=todo, user=request.user, end_time__isnull=True).first()
    if timer:
        timer.end_time = timezone.now()
        timer.save()
    return redirect('todo')

@login_required
def timer_log(request, item_id):
    todo = get_object_or_404(Todo, id=item_id)
    timers = TodoTimer.objects.filter(todo=todo, user=request.user)
    total_time_spent = sum(timer.total_time() for timer in timers)
    return render(request, 'todo/timer_log.html', {'timers': timers, 'total_time_spent': total_time_spent, 'todo': todo})

@login_required
def index(request):
    # Get the search query and sort option from the request
    query = request.GET.get('q', None)
    sort_by = request.GET.get('sort_by', None)

    # Get the user's teams
    user_teams = request.user.teams.all()

    # Retrieve the user's To-Do items and team To-Do items, ensuring no duplicates
    item_list = Todo.objects.filter(
        Q(user=request.user) | Q(team__in=user_teams) | Q(assigned_users=request.user)
    ).distinct()

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

    if request.method == "POST":
        # Pass the current user to the TodoForm for dynamic team queryset
        form = TodoForm(request.POST, user=request.user)  
        if form.is_valid():
            todo_item = form.save(commit=False)
            todo_item.user = request.user  # Assign the creator of the to-do
            todo_item.save()
            form.save_m2m()  # Save the ManyToMany relationships

            return redirect('todo')
    else:
        # Pass the current user to the TodoForm for dynamic team queryset
        form = TodoForm(user=request.user)  

    # Get all users for the create team modal (excluding the current user)
    users = User.objects.exclude(id=request.user.id)

    page = {
        "forms": form,
        "list": item_list,
        "title": "TODO LIST",
        "users": users,
    }
    return render(request, 'todo/index.html', page)


@login_required
def remove(request, item_id):
    # Check if the user is the creator, assigned user, or a team member
    items = Todo.objects.filter(
        Q(id=item_id) & (Q(user=request.user) | Q(assigned_users=request.user) | Q(team__members=request.user))
    )

    if request.method == "POST":
        items.delete()
        messages.info(request, "Item removed!")
        return redirect('todo')
    
    return render(request, 'todo/confirm_delete.html', {'item': items})



@login_required
def edit(request, item_id):
    # First, filter the Todo items based on the provided conditions
    item = Todo.objects.filter(
        Q(id=item_id) & (Q(user=request.user) | Q(assigned_users=request.user) | Q(team__members=request.user))
    ).first()  # Use first() to ensure it only returns one item

    # If no item is found, raise a 404 error
    if not item:
        raise Http404("Todo item not found")

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
    # Fetch the specific Todo item for the given item_id and user constraints
    item = Todo.objects.filter(
        Q(id=item_id) & (Q(user=request.user) | Q(assigned_users=request.user) | Q(team__members=request.user))
    ).first()

    if item:
        # Mark the item as complete and save it
        item.completed = True
        item.save()
        messages.success(request, "Item marked as complete.")
    else:
        messages.error(request, "Todo item not found or you don't have permission to mark it as complete.")

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

@login_required
def create_team(request):
    users = User.objects.all()
    if request.method == 'POST':
        form = TeamForm(request.POST)
        if form.is_valid():
            team = form.save(commit=False)
            team.save() # save the team

            members = form.cleaned_data.get('members')
            if members:
                team.members.add(*members.exclude(id=request.user.id)) # add all selected members
            # add the current user to the team
            team.members.add(request.user)

            return JsonResponse({'success': True})  # Return success response for AJAX
        else: 
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
    else: # if get request then give back empty form (ie page is loaded for first time)
        form = TeamForm()
    return render(request, 'todo/index.html', {'form': form, 'users': users})

@login_required
def user_teams(request):
    teams = request.user.teams.all()  # Fetch teams where the current user is a member
    return render(request, 'todo/user_teams.html', {'teams': teams})


# Update Team view
@login_required
def update_team(request, team_id):
    team = get_object_or_404(Team, id=team_id)
    
    if request.user not in team.members.all():
        messages.error(request, "You are not allowed to update this team.")
        return redirect('user_teams')

    if request.method == 'POST':
        form = TeamForm(request.POST, instance=team)
        if form.is_valid():
            form.save()
            messages.success(request, "Team updated successfully!")
            return redirect('user_teams')
    else:
        form = TeamForm(instance=team)

    return render(request, 'todo/update_team.html', {'form': form, 'team': team})


# Delete Team view with confirmation
@login_required
def delete_team(request, team_id):
    team = get_object_or_404(Team, id=team_id)

    if request.user not in team.members.all():
        messages.error(request, "You are not allowed to delete this team.")
        return redirect('user_teams')

    if request.method == 'POST':
        team.delete()
        messages.success(request, "Team deleted successfully!")
        return redirect('user_teams')

    return render(request, 'todo/delete_team_confirm.html', {'team': team})