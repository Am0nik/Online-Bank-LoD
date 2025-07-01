from django.db import models
import random
from account.models import CustomUser

def generate_account_number():
    prefix = '5510'
    while True:
        suffix = ''.join([str(random.randint(0, 9)) for _ in range(12)])
        account_number = prefix + suffix
        if not Check.objects.filter(account_number=account_number).exists():
            return account_number

def generate_code():
    return ''.join([str(random.randint(0, 9)) for _ in range(3)])

class Check(models.Model):
    account_number = models.CharField(max_length=16, unique=True, blank=True, null=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='checks')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    code = models.CharField(max_length=3, blank=True, null=True)  # <-- добавлено


    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = generate_account_number()
        if not self.code:
            self.code = generate_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Check {self.account_number} - Amount: {self.balance}"

class Transfer(models.Model):
    sender = models.ForeignKey(
        'Check',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_transfers'  # <-- уникальное имя
    )
    recipient = models.ForeignKey(
        'Check',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='received_transfers'  # <-- уникальное имя
    )
    sender_user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_user_transfers'
    )
    recipient_user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='received_user_transfers'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    from_main = models.BooleanField(default=False)
    message = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} → {self.recipient} : {self.amount}₸"
