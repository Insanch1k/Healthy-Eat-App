from django.shortcuts import render, redirect
from .models import Notes
from .forms import AddForm
from django.views.generic.edit import UpdateView
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required


@login_required
def home_notes(request):  
    
    '''Function for showing list of notes'''
    
    user = request.user  
    notes = Notes.objects.filter(owner=user).order_by('-created')  
    if request.method == 'POST':
        add_form = AddForm(request.POST)  
        if add_form.is_valid():  
            new_notes = add_form.save(commit=False)  
            new_notes.owner = request.user  
            new_notes.save() 
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
    
    '''Function for updeting information of notes'''
    
    n = Notes.objects.get(id=id)

    form = AddForm(instance=n)  
    if request.method == 'POST':
        form = AddForm(request.POST, instance=n)
        if form.is_valid(): 
            form.save()  
            return redirect('notes:home_notes')  
    context = { 
        'form': form,
    }
    return render(request, 'notes/notes_update_form.html', context) 


@login_required
def delete(request, id):
    
    '''Function for delete notes'''
    
    item = Notes.objects.get(id=id)
    if request.method == 'POST':
        item.delete()
        return redirect('notes:home_notes')
    context = {
        'item': item,
    }
    return render(request, 'notes/delete.html', context)
