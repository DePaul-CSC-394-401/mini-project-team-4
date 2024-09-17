from django.contrib.auth.decorators import login_required
from django.views.generic.edit import FormView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import TodoForm
from django.db.models import Q
<<<<<<< HEAD
from django.contrib.auth.models import User
from django.views.generic.edit import FormView
from .models import Todo
from django import forms


=======
from .models import Todo
>>>>>>> b81dd9b70b0df2d337ee2359ea362765084c46b4
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
<<<<<<< HEAD
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .models import Todo
=======
>>>>>>> b81dd9b70b0df2d337ee2359ea362765084c46b4

class CustomLoginView(LoginView):
    template_name = 'todo/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('todo')
    
<<<<<<< HEAD
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
=======
>>>>>>> b81dd9b70b0df2d337ee2359ea362765084c46b4
class RegisterPage(FormView):
    template_name = 'todo/register.html'
    form_class = CustomUserCreationForm  # Use the custom form
    redirect_authenticated_user = True
    success_url = reverse_lazy('todo')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)
    
<<<<<<< HEAD
    def get(self,*args, **kwargs):
=======
    def get(self, *args, **kwargs):
>>>>>>> b81dd9b70b0df2d337ee2359ea362765084c46b4
        if self.request.user.is_authenticated:
            return redirect('todo')
        return super(RegisterPage, self).get(*args, **kwargs)

    

@login_required
def index(request):
    # Get the search query and sort option from the request
    query = request.GET.get('q', None)
    sort_by = request.GET.get('sort_by', None)

    # Filter todos by the logged-in user
    item_list = Todo.objects.filter(user=request.user)

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
    }
    return render(request, 'todo/index.html', page)


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
<<<<<<< HEAD


@login_required
def index(request):
    # Get the search query from the request
    query = request.GET.get('q', None)

    # Filter todos by the logged-in user and search query if present
    item_list = Todo.objects.filter(user=request.user).order_by("-date")

    if query:
        # If a search query exists, filter the items by title or description (details)
        item_list = item_list.filter(Q(title__icontains=query) | Q(details__icontains=query))

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
    }
    return render(request, 'todo/index.html', page)

@login_required
def update_email(request):
    if request.method == 'POST':
        new_email = request.POST.get('email')

        # Check if the new email is different from the current email
        if new_email != request.user.email:
            user = request.user
            user.email = new_email
            user.save(update_fields=['email'])  # Only update the email field

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
=======
>>>>>>> b81dd9b70b0df2d337ee2359ea362765084c46b4
