from django.contrib.auth.decorators import login_required
from django.views.generic.edit import FormView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import TodoForm
from django.db.models import Q
from django.contrib.auth.models import User
from django.views.generic.edit import FormView
from .models import Todo
from django import forms

from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login

from .models import Todo

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
    form_class = CustomUserCreationForm  # Use the custom form
    redirect_authenticated_user = True
    success_url = reverse_lazy('todo')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)
    
    def get(self,*args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('todo')
        return super(RegisterPage, self).get(*args, **kwargs)

    

@login_required
def index(request):
    # Filter todos by the logged-in user
    item_list = Todo.objects.filter(user=request.user).order_by("-date")

    if request.method == "POST":
        form = TodoForm(request.POST)
        if form.is_valid():
            # Don't save directly yet, but create an instance without committing to DB
            todo_item = form.save(commit=False)
            # Assign the currently logged-in user to the todo item
            todo_item.user = request.user
            # Now save the todo item to the database
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



### function to remove item, it receive todo item_id as primary key from url ##
@login_required
def remove(request, item_id):
    item = get_object_or_404(Todo, id=item_id, user=request.user)
    item.delete()
    messages.info(request, "item removed !!!")
    return redirect('todo')

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