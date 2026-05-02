from django.contrib import messages
from django.shortcuts import render

from diets.forms import CalculatorForm
from diets.services import calculate_bmr_tdee


def calculator(request):
    if request.method == 'POST':
        form = CalculatorForm(request.POST)
        if form.is_valid():
            return render(request, 'res_for_calculator.html', calculate_bmr_tdee(form.cleaned_data))
        messages.error(request, 'Please correct the calculator data.')
    else:
        form = CalculatorForm()
    return render(request, 'calculator.html', {'form': form})
