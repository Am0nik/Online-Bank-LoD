from django import forms
from .models import CustomUser

class CustomUserCreationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'user', 'surname', 'phone_number', 'email',
            'account_type', 'balance', 'profile_picture'
        ]
        widgets = {
            'password': forms.PasswordInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].label = "Имя"
        self.fields['surname'].label = "Фамилия"
        self.fields['phone_number'].label = "Номер телефона"
        self.fields['email'].label = "Электронная почта"

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
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
