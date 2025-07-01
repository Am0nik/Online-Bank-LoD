from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from .forms import CustomUserCreationForm, AuthenticationForm
from .models import CustomUser
from django.contrib.auth.decorators import login_required
from transfers.models import Check

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            if user is not None:
                login(request, user)
                return redirect('profile')  # или куда тебе нужно
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('profile')  # перенаправление на страницу входа после регистрации
    else:
        form = CustomUserCreationForm()

    return render(request, 'register.html', {'form': form})

@login_required
def profile_view(request):
    user = request.user  # текущий вошедший пользователь
    checks = Check.objects.filter(user=user)  # получение счетов пользователя

    context = {
        'name': user.user,
        'surname': user.surname,
        'email': user.email,
        'phone_number': user.phone_number,
        'account_number': user.account_number,
        'balance': user.balance,
        'account_type': user.account_type,
        'profile_picture': user.profile_picture,
        'code': user.code,
        'checks': checks,
    }

    return render(request, 'profile.html', context)


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')