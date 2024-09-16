from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import TodoForm
from .models import Todo

###############################################


def index(request):
    item_list = Todo.objects.order_by("-date")
    if request.method == "POST":
        form = TodoForm(request.POST)
        if form.is_valid():
            form.save()
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
def remove(request, item_id):
    item = Todo.objects.get(id=item_id)
    item.delete()
    messages.info(request, "item removed !!!")
    return redirect('todo')


def edit(request, item_id):
    item = Todo.objects.get(id=item_id)
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




def mark_complete(request, item_id):
    item = get_object_or_404(Todo, id=item_id)
    item.completed = True
    item.save()
    return redirect('todo')