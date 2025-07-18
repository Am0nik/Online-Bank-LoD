from django.db import models
from account.models import CustomUser
import random
from django.shortcuts import get_object_or_404, redirect, render
from decimal import Decimal
from django.core.validators import RegexValidator

def fine_number_generator():
    while True:
        number = str(random.randint(100000, 99999999999999))
        if not Mulct.objects.filter(fine_number=number).exists():
            return number

def generate_unique_transport_card_number():
    prefix = '55031019'
    while True:
        suffix = ''.join(str(random.randint(0, 9)) for _ in range(8))
        card_number = prefix + suffix
        if not Travel_Card.objects.filter(card_number=card_number).exists():
            return card_number

class Mulct(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    fine_number = models.CharField(max_length=20, unique=True, default=fine_number_generator)
    is_paid = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def pay(self, paying_user):
        if self.is_paid:
            raise ValueError("Штраф уже оплачен")
        if self.user != paying_user:
            raise PermissionError("Вы не можете оплатить чужой штраф")
        self.is_paid = True
        self.save()

class HCS(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    hcs_number = models.CharField(max_length=20, unique=True, default=fine_number_generator)
    is_paid = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def pay(self, paying_user):
        if self.is_paid:
            raise ValueError("Платёж уже произведён")
        if self.user != paying_user:
            raise PermissionError("Вы не можете оплатить чужой платёж")
        self.is_paid = True
        self.save()


class Parking(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    parking_number = models.CharField(
        max_length=4,
        validators=[RegexValidator(r'^\d{4}$', message='Номер парковки должен содержать ровно 4 цифры')]
    )
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Парковка {self.parking_number}"


class Travel_Card(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    card_number = models.CharField(max_length=16, unique=True, default=generate_unique_transport_card_number)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    is_active = models.BooleanField(default=True)

