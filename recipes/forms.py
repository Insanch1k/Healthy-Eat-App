from django import forms
from django.contrib.auth.models import User

from .models import Profile


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Enter password...'}
        )
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Repeat password...'}
        )
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'email')

        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Enter your username...'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Enter your first name...'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 'placeholder': 'Enter your email...'
            })
        }

    def clean_password2(self):
        cd = self.cleaned_data
        if cd.get('password') != cd.get('password2'):
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('A user with this email already exists.')
        return email


class EditUser(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Enter your username...'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Enter your first name...'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 'placeholder': 'Enter your email...'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Enter your last name...'
            })
        }


class EditProfile(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('phone',)

        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Your phone number..'
            })
        }
