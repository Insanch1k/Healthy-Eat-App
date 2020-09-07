from django import forms
from .models import Weight
from .models import Weight, Diet


class WeightForm(forms.ModelForm):
    class Meta:
        model = Weight
        fields = ('weight',)
        labels = {
            'weight': 'Your current weight: ',
        }
        widgets = {
            'weight': forms.NumberInput(attrs={
                'step': '0.1', 'class': 'form-control', 'min': '0'
            })
        }


class UpdateAmounts(forms.ModelForm):
    class Meta:
        model = Diet
        fields = ('amount_of_lunch',)

        widgets = {
            'amount_of_lunch': forms.NumberInput(attrs={
                'class': 'form-control'
            })
        }
