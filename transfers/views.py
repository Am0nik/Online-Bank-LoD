from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import Check, Transfer
from account.models import CustomUser
from decimal import Decimal
from django.contrib import messages
from decimal import Decimal

# Create your views here.
@login_required
def transfers(request):

    checks = Check.objects.filter(user=request.user)
    transfers = Transfer.objects.filter(sender__in=checks).order_by('-timestamp')

    context = {
        'user': request.user,
        'checks': checks,
        'transfers': transfers,
    }
    
    return render(request, 'transfer.html', context)



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

@transaction.atomic
def transfer_by_account_number(sender_check, recipient_account_number, amount, message=''):
    try:
        recipient_account_number = CustomUser.objects.get(account_number=recipient_account_number)
    except CustomUser.DoesNotExist:
        raise ValueError("Пользователь с таким номером не найден")

    try:
        recipient_check = Check.objects.filter(user=recipient_account_number).first()
    except Check.DoesNotExist:
        raise ValueError("У получателя нет счёта")

    if sender_check.user == recipient_account_number:
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
def transfer_by_account_view(request):
    if request.method == 'POST':
        sender_check_id = request.POST.get('sender_check_id')
        recipient_account_number = request.POST.get('account_number')
        amount = float(request.POST.get('amount'))
        description = request.POST.get('description')

        try:
            recipient_user = CustomUser.objects.get(account_number=recipient_account_number)
        except CustomUser.DoesNotExist:
            messages.error(request, "Получатель не найден.")
            return redirect('transfers')

        # === Основной счёт ===
        if sender_check_id == "main":
            if request.user.balance < amount:
                messages.error(request, "Недостаточно средств на основном счёте.")
                return redirect('transfers')

            # Списание и начисление
            request.user.balance -= amount
            recipient_user.balance += amount
            request.user.save()
            recipient_user.save()

            Transfer.objects.create(
                sender_user=request.user,
                recipient_user=recipient_user,
                amount=amount,
                message=description,
                from_main=True
            )

        # === Дополнительный счёт ===
        else:
            try:
                sender_check = Check.objects.get(id=sender_check_id, user=request.user)
            except Check.DoesNotExist:
                messages.error(request, "Счёт не найден.")
                return redirect('transfers')

            if sender_check.balance < amount:
                messages.error(request, "Недостаточно средств на выбранном счёте.")
                return redirect('transfers')

            sender_check.balance -= amount
            recipient_user.balance += amount
            sender_check.save()
            recipient_user.save()

            Transfer.objects.create(
                sender=sender_check,
                sender_user=request.user,
                recipient_user=recipient_user,
                amount=amount,
                message=description,
                from_main=False
            )

        messages.success(request, "Перевод выполнен успешно.")
        return redirect('transfers')
@login_required
def transfer_by_account_view(request):
    if request.method == 'POST':
        sender_check_id = request.POST.get('sender_check_id')
        recipient_account_number = request.POST.get('account_number')
        amount = Decimal(request.POST.get('amount'))
        description = request.POST.get('description')

        try:
            recipient_user = CustomUser.objects.get(account_number=recipient_account_number)
        except CustomUser.DoesNotExist:
            messages.error(request, "Получатель не найден либо вы пытаетесь перевести средства самому себе на свой же счёт.")
            return redirect('transfers')

        # === Основной счёт ===
        if sender_check_id == "main":
            if request.user.balance < amount:
                messages.error(request, "Недостаточно средств на основном счёте.")
                return redirect('transfers')

            # Списание и начисление
            request.user.balance -= amount
            recipient_user.balance += amount
            request.user.save()
            recipient_user.save()

            Transfer.objects.create(
                sender_user=request.user,
                recipient_user=recipient_user,
                amount=amount,
                message=description,
                from_main=True
            )

        # === Дополнительный счёт ===
        else:
            try:
                sender_check = Check.objects.get(id=sender_check_id, user=request.user)
            except Check.DoesNotExist:
                messages.error(request, "Счёт не найден.")
                return redirect('transfers')

            if sender_check.balance < amount:
                messages.error(request, "Недостаточно средств на выбранном счёте.")
                return redirect('transfers')

            sender_check.balance -= amount
            recipient_user.balance += amount
            sender_check.save()
            recipient_user.save()

            Transfer.objects.create(
                sender=sender_check,
                sender_user=request.user,
                recipient_user=recipient_user,
                amount=amount,
                message=description,
                from_main=False
            )

        messages.success(request, "Перевод выполнен успешно.")
        return redirect('transfers')




