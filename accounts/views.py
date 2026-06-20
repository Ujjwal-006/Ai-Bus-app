from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm, ProfileUpdateForm
from transit.models import Profile, Wallet


def register_view(request):
    if request.user.is_authenticated:
        return redirect('transit:schedules')
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Wallet.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('transit:schedules')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('transit:schedules')
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('transit:schedules')
        else:
            messages.error(request, 'Invalid email or password.')
    else:
        form = UserLoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('transit:login_user')


@login_required
def account_settings_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('transit:account_settings')
    else:
        form = ProfileUpdateForm(instance=profile)
    return render(request, 'accounts/account_settings.html', {
        'form': form,
        'profile': profile,
    })


def forgot_password_view(request):
    return render(request, 'accounts/forgot_password.html')


def reset_password_view(request):
    return render(request, 'accounts/reset_password.html')
