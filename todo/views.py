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
from django.contrib.auth import login

class CustomLoginView(LoginView):
    template_name = 'todo/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('todo')
    
class RegisterPage(FormView):
    template_name = 'todo/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('todo')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)
    
    def get(self, *args, **kwargs):
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
