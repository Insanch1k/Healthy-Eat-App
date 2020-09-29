from django import  forms
from .models import Notes


'''Form for adding new notes'''

class AddForm(forms.ModelForm):
    class Meta:
        model = Notes
        fields = ['title', 'body']

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'title...'
            }),
            'body': forms.Textarea(attrs={
                'class': 'form-control', 'placeholder': 'body..'
            })
        }


