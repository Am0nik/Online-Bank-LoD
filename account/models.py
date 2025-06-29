from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
import random

def generate_account_number():
    prefix = '5510'
    while True:
        suffix = ''.join([str(random.randint(0, 9)) for _ in range(12)])
        account_number = prefix + suffix
        if not CustomUser.objects.filter(account_number=account_number).exists():
            return account_number




class CustomUserManager(BaseUserManager):
    def create_user(self, user, password=None, **extra_fields):
        if not user:
            raise ValueError("Поле 'user' обязательно.")
        user_instance = self.model(user=user, **extra_fields)
        user_instance.set_password(password)
        user_instance.save()
        return user_instance

    def create_superuser(self, user, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not password:
            raise ValueError("Суперпользователь должен иметь пароль.")

        return self.create_user(user, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    user = models.CharField(max_length=150, unique=True)
    surname = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)
    account_number = models.CharField(max_length=16, unique=True, editable=False)
    account_type = models.CharField(max_length=50, choices=[
        ('client', 'Client'),
        ('moderator', 'Moderator'),
    ], default='client', blank=True, null=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True, null=True)
    password = models.CharField(max_length=128, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    code = models.CharField(max_length=6)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'user'
    REQUIRED_FIELDS = ['surname', 'phone_number', 'email', 'account_type', 'balance','password']

    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = generate_account_number()
        if not self.code:
            self.code = ''.join([str(random.randint(0, 9)) for _ in range(6)])


        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.user} - {self.account_number}"
