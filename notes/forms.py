from django import forms

from .models import Note


class AddForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['title', 'body']

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'title...'
            }),
            'body': forms.Textarea(attrs={
                'class': 'form-control', 'placeholder': 'body..'
            })
        }

