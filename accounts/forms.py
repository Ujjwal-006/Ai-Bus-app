from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from transit.models import Profile


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'w-full bg-secondary-fixed/20 border border-outline-variant/30 rounded px-4 py-3 text-body-md focus:outline-none focus:border-secondary transition-all placeholder:text-outline-variant/60',
        'placeholder': 'name@company.com'
    }))
    full_name = forms.CharField(max_length=200, required=True, widget=forms.TextInput(attrs={
        'class': 'w-full bg-secondary-fixed/20 border border-outline-variant/30 rounded px-4 py-3 text-body-md focus:outline-none focus:border-secondary transition-all placeholder:text-outline-variant/60',
        'placeholder': 'John Doe'
    }))

    class Meta:
        model = User
        fields = ['username', 'email', 'full_name', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'w-full bg-secondary-fixed/20 border border-outline-variant/30 rounded px-4 py-3 text-body-md focus:outline-none focus:border-secondary transition-all placeholder:text-outline-variant/60',
            'placeholder': 'username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'w-full bg-secondary-fixed/20 border border-outline-variant/30 rounded px-4 py-3 text-body-md focus:outline-none focus:border-secondary transition-all placeholder:text-outline-variant/60',
            'placeholder': 'Enter password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'w-full bg-secondary-fixed/20 border border-outline-variant/30 rounded px-4 py-3 text-body-md focus:outline-none focus:border-secondary transition-all placeholder:text-outline-variant/60',
            'placeholder': 'Confirm password'
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            Profile.objects.create(
                user=user,
                full_name=self.cleaned_data['full_name']
            )
        return user


class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'w-full bg-secondary-fixed/20 border border-outline-variant/30 rounded px-4 py-3 text-body-md focus:outline-none focus:border-secondary transition-all placeholder:text-outline-variant/60',
        'placeholder': 'name@company.com'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'w-full bg-secondary-fixed/20 border border-outline-variant/30 rounded px-4 py-3 text-body-md focus:outline-none focus:border-secondary transition-all placeholder:text-outline-variant/60',
        'placeholder': '••••••••'
    }))


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['full_name', 'phone', 'timezone_val', 'profile_picture']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'w-full p-4 bg-transparent border border-outline-variant/20 text-body-md text-primary focus:border-secondary focus:outline-none'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full p-4 bg-transparent border border-outline-variant/20 text-body-md text-primary focus:border-secondary focus:outline-none'
            }),
            'timezone_val': forms.Select(attrs={
                'class': 'w-full p-4 bg-transparent border border-outline-variant/20 text-body-md text-primary focus:border-secondary focus:outline-none'
            }),
        }
