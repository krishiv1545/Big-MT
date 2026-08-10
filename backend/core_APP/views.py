from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages


# ── Auth views ───────────────────────────────────────────────────────────────

def login_view(request):
    """GET: show login form.  POST: authenticate and redirect to dashboard."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        remember = request.POST.get('remember')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if not remember:
                request.session.set_expiry(0)  # session expires on browser close
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'core_APP/login.html')


def signup_view(request):
    """GET: show signup form.  POST: create user, redirect to login."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        confirm = request.POST.get('confirm', '')

        if not username or not password:
            messages.error(request, 'Username and password are required.')
        elif password != confirm:
            messages.error(request, 'Passwords do not match.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
        else:
            User.objects.create_user(username=username, password=password)
            messages.success(request, 'Account created! Please log in.')
            return redirect('login')

    return render(request, 'core_APP/signup.html')


def logout_view(request):
    """Log out and redirect to login page."""
    logout(request)
    return redirect('login')


# ── Views ──────────────────────────────────────────────────────────

@login_required
def dashboard_view(request):
    return render(request, 'core_APP/dashboard.html')


@login_required
def settings_view(request):
    return render(request, 'core_APP/settings.html')
