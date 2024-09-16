from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import TodoForm

from django.contrib.auth.views import LoginView

from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Todo

class CustomLoginView(LoginView):
    template_name = 'todo/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('todo')

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