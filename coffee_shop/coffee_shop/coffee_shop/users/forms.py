from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'placeholder': 'example@mail.com'
    }))
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': '+7 (999) 123-45-67'
    }))
    address = forms.CharField(required=False, widget=forms.Textarea(attrs={
        'rows': 3,
        'placeholder': 'Ваш адрес для доставки'
    }))

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'phone', 'address')
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Придумайте логин'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'placeholder': 'Не менее 8 символов'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Повторите пароль'})