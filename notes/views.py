from django.shortcuts import render, redirect
from .models import Notes
from .forms import AddForm
from django.views.generic.edit import UpdateView
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required


@login_required
def home_notes(request):  # wyswietlenie wszystkich notatek
    user = request.user  # zalogowany uzytkownik
    notes = Notes.objects.filter(owner=user).order_by('-created')  # wszystkie notatki dla zalogowanego uzytkownika
    if request.method == 'POST':
        add_form = AddForm(request.POST)  # forma da dodania nowych notatek
        if add_form.is_valid():  # jeski forma walidowana
            new_notes = add_form.save(commit=False)  # bierzemy dane ale nie zachowuhemy w bazie
            new_notes.owner = request.user  # przepisujemy wlasciciela
            new_notes.save()  # zacowujemy w bazie
        return redirect('notes:home_notes')  # lecimy na strone gdzie sa wszystkie notatki
    else:
        add_form = AddForm()  # pusta forma
    context = {  # przekazyjemy dane w HTML
        'notes': notes,
        'add_form': add_form,
    }
    return render(request, 'notes/notes_main.html', context)  # przekazyjemy dane w HTML


@login_required
def update_notes(request, id):  # edycja notatek
    n = Notes.objects.get(id=id)  # bierzemy notatke za pomoca id

    form = AddForm(instance=n)  # forma dla edycji
    if request.method == 'POST':
        form = AddForm(request.POST, instance=n)  # wyswietlamy stare dane
        if form.is_valid():  # jesli forma walidowana
            form.save()  # zachowujemy w bazie
            return redirect('notes:home_notes')  # lecimy na strone gdzie sa wszystkie notatki
    context = {  # przekazyjemy dane w HTML
        'form': form,
    }
    return render(request, 'notes/notes_update_form.html', context)  # przekazyjemy dane w HTML


@login_required
def delete(request, id):
    item = Notes.objects.get(id=id)
    if request.method == 'POST':
        item.delete()
        return redirect('notes:home_notes')
    context = {
        'item': item,
    }
    return render(request, 'notes/delete.html', context)
