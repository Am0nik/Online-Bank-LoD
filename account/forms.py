from django import forms
from .models import CustomUser
import re

class CustomUserCreationForm(forms.ModelForm):

    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={'placeholder': 'Введите пароль', 'class': 'custom-input'})
    )

    class Meta:
        model = CustomUser
        fields = [
            'user', 'surname', 'phone_number', 'email',
            'account_type', 'balance', 'profile_picture'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].label = "Имя"
        self.fields['user'].widget.attrs.update({'placeholder': 'Введите имя', 'class': 'custom-input'})

        self.fields['surname'].label = "Фамилия"
        self.fields['surname'].widget.attrs.update({'placeholder': 'Введите фамилию', 'class': 'custom-input'})

        self.fields['phone_number'].label = "Номер телефона"
        self.fields['phone_number'].widget.attrs.update({'placeholder': 'Введите номер телефона', 'class': 'custom-input'})

        self.fields['email'].label = "Электронная почта"
        self.fields['email'].widget.attrs.update({'placeholder': 'Введите электронную почту', 'class': 'custom-input'})


    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        phone_number = phone_number.replace('+', '')
        if not phone_number.isdigit() or len(phone_number) < 10:
            raise forms.ValidationError("Номер телфона должен содержать только цифры и быть не менее 10 цифр.")
        return phone_number

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = CustomUser.objects.filter(email=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Эта почта уже используется")
        return email
    
    def clean_password(self):
        password = self.cleaned_data.get('password')

        if len(password) < 8:
            raise forms.ValidationError("Пароль должен быть не менее 8 символов.")
        if not re.search(r"[A-ZА-Я]", password):
            raise forms.ValidationError("Пароль должен содержать хотя бы одну заглавную букву.")
        if not re.search(r"[a-zа-я]", password):
            raise forms.ValidationError("Пароль должен содержать хотя бы одну строчную букву.")
        if not re.search(r"[0-9]", password):
            raise forms.ValidationError("Пароль должен содержать хотя бы одну цифру.")
        if not re.search(r"[!@#$%^&*()_+{}\[\]:;<>,.?~\\/-]", password):
            raise forms.ValidationError("Пароль должен содержать хотя бы один специальный символ.")

        return password

from django import forms
from django.contrib.auth.hashers import check_password
from .models import CustomUser

class AuthenticationForm(forms.Form):
    user = forms.CharField(
        label="Имя",
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Введите имя', 'class': 'custom-input'})
    )
    surname = forms.CharField(
        label="Фамилия",
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Введите фамилию','class': 'custom-input'})
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={'placeholder': 'Введите пароль','class': 'custom-input'})
    )

    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get("user")
        password = cleaned_data.get("password")
        surname = cleaned_data.get("surname")

        if user and password and surname:
            try:
                self.user_obj = CustomUser.objects.get(user=user)
                if self.user_obj.surname != surname:
                    raise forms.ValidationError("Неверное имя, фамилия или пароль")
                if not self.user_obj.check_password(password):
                    raise forms.ValidationError("Неверный имя, фамилия или пароль")
            except CustomUser.DoesNotExist:
                raise forms.ValidationError("Пользователь не найден")
        return cleaned_data

    def get_user(self):
        return getattr(self, "user_obj", None)
