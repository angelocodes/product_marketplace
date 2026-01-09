from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.urls import reverse


def login_view(request):
    """Custom login view with nice template"""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                next_url = request.GET.get('next', 'dashboard')
                return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {
        'form': form,
        'next': request.GET.get('next', '')
    })


def logout_view(request):
    """Custom logout view"""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login')


def dashboard_view(request):
    """Simple dashboard after login"""
    if not request.user.is_authenticated:
        return redirect('login')

    context = {
        'user': request.user,
        'business': getattr(request.user, 'business', None),
        'role': getattr(request.user, 'role', 'user'),
    }

    return render(request, 'dashboard.html', context)