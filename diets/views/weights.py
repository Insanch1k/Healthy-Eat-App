from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from diets import selectors
from diets.forms import WeightForm
from diets.services import (
    DuplicateWeightForDateError,
    create_weight_entry,
    user_has_weight_today,
)


@login_required
def show_progress(request):
    my_weight = selectors.weights_for_user(request.user)
    first_weight = my_weight.first()
    last_weight = my_weight.last()
    progress = None
    if first_weight and last_weight and first_weight.id != last_weight.id:
        progress = round(float(last_weight.weight) - float(first_weight.weight), 2)

    if request.method == 'POST':
        weight_form = WeightForm(request.POST)
        if user_has_weight_today(request.user):
            messages.warning(request, 'Today you already added your weight')
            return redirect('diets:weight')
        if weight_form.is_valid():
            try:
                create_weight_entry(request.user, weight_form.cleaned_data['weight'])
            except DuplicateWeightForDateError:
                messages.warning(request, 'Today you already added your weight')
            return redirect('diets:weight')
    else:
        weight_form = WeightForm()

    labels = [entry.date.isoformat() for entry in my_weight]
    values = [float(entry.weight) for entry in my_weight]
    context = {
        'weight_form': weight_form,
        'weight': my_weight,
        'last': last_weight,
        'first': first_weight,
        'res': progress,
        'chart_labels': labels,
        'chart_values': values,
    }
    return render(request, 'weight/weight_progress.html', context)


@login_required
def delete_weight(request, id):
    item = selectors.get_weight_for_user(user=request.user, weight_id=id)
    if request.method == 'POST':
        item.delete()
        return redirect('diets:weight')
    return render(request, 'weight/weight_delete.html', {'weight_for_delete': item})
