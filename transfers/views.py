from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import Check, Transfer
from account.models import CustomUser
from django.contrib import messages
from decimal import Decimal

# Create your views here.
@login_required
def transfers(request):

    cheks = Check.objects.filter(user=request.user)

    context = {
        'user': request.user,
        'cheks': cheks,
    }
    
    return render(request, 'transfer.html', context)

@login_required
def transfers_history(request):
    cheks = Check.objects.filter(user=request.user)

    context = {
        'user': request.user,
        'cheks': cheks,
    }
    
    return render(request, 'history_transfers.html', context)




@transaction.atomic
def transfer_by_phone(sender_check, recipient_phone_number, amount, message=''):
    try:
        recipient_user = CustomUser.objects.get(phone_number=recipient_phone_number)
    except CustomUser.DoesNotExist:
        raise ValueError("Пользователь с таким номером не найден")

    try:
        recipient_check = Check.objects.filter(user=recipient_user).first()
    except Check.DoesNotExist:
        raise ValueError("У получателя нет счёта")

    if sender_check.user == recipient_user:
        raise ValueError("Нельзя перевести самому себе")

    if sender_check.balance < amount:
        print(sender_check.balance, amount)
        raise ValueError("Недостаточно средств")

    # Обновляем балансы
    sender_check.balance -= amount
    recipient_check.balance += amount
    sender_check.save()
    recipient_check.save()

    # Создаём запись перевода
    Transfer.objects.create(
        sender=sender_check,
        recipient=recipient_check,
        amount=amount,
        message=message  # если хочешь сохранить текст
    )



@login_required
def transfer_by_phone_view(request):
    if request.method == 'POST':
        sender_id = request.POST.get('sender_check_id')
        phone = request.POST.get('phone')
        phone = phone.replace(' ', '').replace('+', '')  # Удаляем пробелы и символы +
        phone = phone.replace('(', '').replace(')', '')  # Удаляем скоб
        amount = Decimal(request.POST.get('amount'))


        try:
            if sender_id == "main":
                # Перевод с основного счёта пользователя
                if request.user.balance < amount:
                    raise ValueError("Недостаточно средств на основном счёте")

                request.user.balance -= amount
                request.user.save()

                recipient_user = CustomUser.objects.get(phone_number=phone)
                if recipient_user == request.user:
                    raise ValueError("Нельзя перевести самому себе")

                recipient_user.balance += amount
                recipient_user.save()

                Transfer.objects.create(
                    sender_user=request.user,
                    recipient_user=recipient_user,
                    sender=None,
                    amount=amount,
                    from_main=True
                )

            else:
                # Перевод с выбранного Check-счета
                sender_check = get_object_or_404(Check, id=sender_id, user=request.user)

                if sender_check.balance < amount:
                    raise ValueError("Недостаточно средств на выбранном счёте")

                recipient_user = CustomUser.objects.get(phone_number=phone)
                if recipient_user == request.user:
                    raise ValueError("Нельзя перевести самому себе")

                sender_check.balance -= amount
                sender_check.save()

                recipient_user.balance += amount
                recipient_user.save()

                Transfer.objects.create(
                    sender_user=request.user,
                    recipient_user=recipient_user,
                    sender=sender_check,
                    amount=amount,
                    from_main=False
                )

            messages.success(request, "Перевод выполнен успешно")

        except CustomUser.DoesNotExist:
            messages.error(request, "Пользователь с таким номером не найден")
        except ValueError as e:
            messages.error(request, str(e))

    return redirect('transfers')


@login_required
def transfer_history_view(request):
    user = request.user
    checks = Check.objects.filter(user=user)
    transfers = Transfer.objects.filter(sender__in=checks).order_by('-timestamp')

    return render(request, 'transfer_history.html', {'transfers': transfers})
