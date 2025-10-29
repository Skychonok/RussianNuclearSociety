from django.shortcuts import render
from django.http import HttpResponse


def home_page(request):
    return render(request, 'main/home.html')

def educ_page(request):
    return render(request, 'main/educ.html')

def events_page(request):
    return render(request, 'main/events.html')

def materials_page(request):
    return render(request, 'main/materials.html')

def about_us_page(request):
    return render(request, 'main/about_us.html')

def login_page(request):
    return render(request, 'main/login.html')

def register_page(request):
    return render(request, 'main/register.html')

def profile_view(request):
    return render(request, 'main/profile.html')