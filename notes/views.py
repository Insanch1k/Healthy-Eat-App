from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AddForm
from .models import Note


@login_required
def home_notes(request):
    notes = request.user.notes.order_by('-created')
    if request.method == 'POST':
        add_form = AddForm(request.POST)
        if add_form.is_valid():
            new_note = add_form.save(commit=False)
            new_note.owner = request.user
            new_note.save()
        return redirect('notes:home_notes')
    else:
        add_form = AddForm()
    context = {
        'notes': notes,
        'add_form': add_form,
    }
    return render(request, 'notes/notes_main.html', context)


@login_required
def update_notes(request, id):
    note = get_object_or_404(Note, id=id, owner=request.user)

    form = AddForm(instance=note)
    if request.method == 'POST':
        form = AddForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            return redirect('notes:home_notes')
    context = {
        'form': form,
    }
    return render(request, 'notes/notes_update_form.html', context)


@login_required
def delete(request, id):
    item = get_object_or_404(Note, id=id, owner=request.user)
    if request.method == 'POST':
        item.delete()
        return redirect('notes:home_notes')
    context = {
        'item': item,
    }
    return render(request, 'notes/delete.html', context)
