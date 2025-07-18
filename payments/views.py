from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal
from .models import Mulct, HCS, Parking, Travel_Card
from transfers.models import Check
from decimal import Decimal



@login_required
def payment_view(request):
    user = request.user
    mulct = Mulct.objects.filter(user=user, is_paid=False).first()  # показываем только не оплаченный
    hcs = HCS.objects.filter(user=user, is_paid=False).first()  # показываем только не оплаченный
    parking = Parking.objects.filter(user=user).first()  # показываем только последнюю парковку
    checks = Check.objects.filter(user=user)
    return render(request, 'payments.html', {
        'mulct': mulct,
        'hcs': hcs,
        'parking': parking,
        'checks': checks,
    })


@login_required
def pay_fine_view(request):
    if request.method == 'POST':
        fine_id = request.POST.get('fine_id')
        sender_check_id = request.POST.get('sender_check_id')

        mulct = get_object_or_404(Mulct, id=fine_id, user=request.user, is_paid=False)
        amount = mulct.amount
        fine_account = get_object_or_404(Check, account_number='Fine')

        if sender_check_id == "main":
            if request.user.balance < amount:
                messages.error(request, "Недостаточно средств на основном счёте.")
            else:
                request.user.balance -= amount
                request.user.save()
                fine_account.balance += amount
                fine_account.save()
                mulct.is_paid = True
                mulct.save()
                messages.success(request, "Штраф успешно оплачен с основного счёта!")
        else:
            check = get_object_or_404(Check, id=sender_check_id, user=request.user)
            if check.balance < amount:
                messages.error(request, "Недостаточно средств на выбранном счёте.")
            else:
                check.balance -= amount
                check.save()
                fine_account.balance += amount
                fine_account.save()
                mulct.is_paid = True
                mulct.save()
                messages.success(request, "Штраф успешно оплачен с дополнительного счёта!")

    return redirect('payment_view')


@login_required
def pay_hcs_view(request):
    if request.method == 'POST':
        hcs_id = request.POST.get('hcs_id')
        sender_check_id = request.POST.get('sender_check_id')

        hcs = get_object_or_404(HCS, id=hcs_id, user=request.user, is_paid=False)
        amount = hcs.amount
        hcs_account = get_object_or_404(Check, account_number='HCS')

        if sender_check_id == "main":
            if request.user.balance < amount:
                messages.error(request, "Недостаточно средств на основном счёте.")
            else:
                request.user.balance -= amount
                request.user.save()
                hcs_account.balance += amount
                hcs_account.save()
                hcs.is_paid = True
                hcs.save()
                messages.success(request, "Платёж успешно выполнен с основного счёта!")
        else:
            check = get_object_or_404(Check, id=sender_check_id, user=request.user)
            if check.balance < amount:
                messages.error(request, "Недостаточно средств на выбранном счёте.")
            else:
                check.balance -= amount
                check.save()
                hcs_account.balance += amount
                hcs_account.save()
                hcs.is_paid = True
                hcs.save()
                messages.success(request, "Платёж успешно выполнен с дополнительного счёта!")

    return redirect('payment_view')

@login_required
def pay_parking_view(request):
    if request.method == 'POST':
        sender_check_id = request.POST.get('sender_check_id')
        amount = request.POST.get('amount')
        parking_number = request.POST.get('number_parking_code')

        # Проверка номера парковки
        if not parking_number or not parking_number.isdigit() or len(parking_number) > 4:
            messages.error(request, "Номер парковки должен быть числом до 4 знаков (например, 0001).")
            return redirect('payment_view')

        try:
            amount = Decimal(amount)
        except:
            messages.error(request, "Некорректная сумма.")
            return redirect('payment_view')

        # Получаем Parking
        try:
            parking_check = Check.objects.get(account_number='Parking')
        except Check.DoesNotExist:
            messages.error(request, "Счёт 'Parking' не найден. Обратитесь к администратору.")
            return redirect('payment_view')

        # Списываем
        if sender_check_id == 'main':
            if request.user.balance < amount:
                messages.error(request, "Недостаточно средств на основном счёте.")
                return redirect('payment_view')
            request.user.balance -= amount
            request.user.save()
        else:
            check = get_object_or_404(Check, id=sender_check_id, user=request.user)
            if check.balance < amount:
                messages.error(request, "Недостаточно средств на выбранном счёте.")
                return redirect('payment_view')
            check.balance -= amount
            check.save()

        # Переводим на счёт Parking
        parking_check.balance += amount
        parking_check.save()

        # Сохраняем саму оплату в истории
        Parking.objects.create(
            user=request.user,
            amount=amount,
            parking_number=parking_number.zfill(4)
        )

        messages.success(request, "Оплата парковки прошла успешно.")
        return redirect('payment_view')
    
@login_required
def transfer_to_eco_view(request):
    if request.method == 'POST':
        sender_check_id = request.POST.get('sender_check_id')
        amount_str = request.POST.get('amount')

        try:
            amount = Decimal(amount_str)
        except:
            messages.error(request, "Неверная сумма.")
            return redirect('payment_view')

        if amount <= 0:
            messages.error(request, "Сумма должна быть больше 0.")
            return redirect('payment_view')

        eco_check = get_object_or_404(Check, account_number='ECO')

        if sender_check_id == 'main':
            if request.user.balance < amount:
                messages.error(request, "Недостаточно средств на основном счёте.")
            else:
                request.user.balance -= amount
                request.user.save()
                eco_check.balance += amount
                eco_check.save()
                messages.success(request, f"Перевод на счёт Эко фонда успешно выполнен!")
        else:
            check = get_object_or_404(Check, id=sender_check_id, user=request.user)
            if check.balance < amount:
                messages.error(request, "Недостаточно средств на выбранном счёте.")
            else:
                check.balance -= amount
                check.save()
                eco_check.balance += amount
                eco_check.save()
                messages.success(request, f"Перевод на счёт Эко фонда ({parking_code}) успешно выполнен!")

    return redirect('payment_view')

def payment_travel_card(request):
    if request.method == 'POST':
        sender_check_id = request.POST.get('sender_check_id')
        amount_str = request.POST.get('amount')
        card_number = request.POST.get('card_number')
        
        try:
            amount = Decimal(amount_str)
        except:
            messages.error(request, "Неверная сумма.")
            return redirect('payment_view')

        if amount <= 0:
            messages.error(request, "Сумма должна быть больше 0.")
            return redirect('payment_view')

        travel_card = get_object_or_404(Travel_Card, card_number=card_number, user=request.user)
        print(f"Travel Card: {travel_card}")
        if sender_check_id == 'main':
            print("Main account selected")
            if request.user.balance < amount:
                messages.error(request, "Недостаточно средств на основном счёте.")
            else:
                request.user.balance -= amount
                request.user.save()
                travel_card.balance += amount
                travel_card.save()
                messages.success(request, f"Пополнение проездного успешно выполнено!")
        else:
            check = get_object_or_404(Check, id=sender_check_id, user=request.user)
            if check.balance < amount:
                messages.error(request, "Недостаточно средств на выбранном счёте.")
            else:
                check.balance -= amount
                check.save()
                travel_card.balance += amount
                travel_card.save()
                messages.success(request, f"Пополнение проездного успешно выполнено!")

    return redirect('payment_view')