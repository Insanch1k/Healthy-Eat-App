from django import forms

from .models import Weight


class CalculatorForm(forms.Form):
    ACTIVITY_CHOICES = [
        ('1.9', 'Hard exercise 2 or more times per day'),
        ('1.725', 'Very active'),
        ('1.55', 'Moderately active'),
        ('1.375', 'Lightly active'),
        ('1.2', 'Sedentary'),
    ]
    SEX_CHOICES = [
        ('Man', 'Man'),
        ('Woman', 'Woman'),
    ]

    age = forms.IntegerField(min_value=18, max_value=100)
    sex = forms.ChoiceField(choices=SEX_CHOICES)
    height = forms.DecimalField(min_value=100, max_value=250, decimal_places=1, max_digits=4)
    weight = forms.DecimalField(min_value=30, max_value=300, decimal_places=1, max_digits=4)
    drop = forms.ChoiceField(choices=ACTIVITY_CHOICES)


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

    def clean_weight(self):
        weight = self.cleaned_data['weight']
        if weight <= 0:
            raise forms.ValidationError('Weight must be greater than zero.')
        return weight


class DietSubscriptionForm(forms.Form):
    breakfast_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    lunch_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    dinner_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
