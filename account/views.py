from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from .forms import CustomUserCreationForm, AuthenticationForm
from .models import CustomUser
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['user']
            password = form.cleaned_data['password']
            # surname уже проверяется в form.clean()
            
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('profile')  # если у тебя есть name='profile' в urls.py
            else:
                form.add_error(None, 'Неверное имя пользователя или пароль')
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})
def register_view(request):
    return render(request, 'register.html')

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('login')  # перенаправление на страницу входа после регистрации
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'profile.html', {'form': form})