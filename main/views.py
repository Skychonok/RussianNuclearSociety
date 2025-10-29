from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages


def home(request):
    """Main page view"""
    return render(request, 'main/home.html')


def about(request):
    """About us page view"""
    return render(request, 'main/about_us.html')


def education(request):
    """Education and career page view"""
    return render(request, 'main/educ.html')


def materials(request):
    """Materials page view"""
    return render(request, 'main/materials.html')


def login_view(request):
    """Login page view"""
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Try to find user by email
        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                login(request, user)
                return redirect('main:home')
            else:
                messages.error(request, 'Неверный пароль')
        except User.DoesNotExist:
            messages.error(request, 'Пользователь с такой почтой не найден')
    
    return render(request, 'main/login.html')


def register_view(request):
    """Registration page view"""
    if request.method == 'POST':
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        # Validate passwords match
        if password != password_confirm:
            messages.error(request, 'Пароли не совпадают')
            return render(request, 'main/register.html')
        
        # Check if user with this email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Пользователь с такой почтой уже существует')
            return render(request, 'main/register.html')
        
        # Create user (username will be email)
        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            login(request, user)
            messages.success(request, 'Регистрация успешно завершена!')
            return redirect('main:home')
        except Exception as e:
            messages.error(request, 'Ошибка при регистрации')
    
    return render(request, 'main/register.html')


def logout_view(request):
    """Logout view"""
    logout(request)
    return redirect('main:home')


# Legacy function names for backward compatibility
def main(request):
    return home(request)

def registration(request):
    return register_view(request)

def login(request):
    return login_view(request)
