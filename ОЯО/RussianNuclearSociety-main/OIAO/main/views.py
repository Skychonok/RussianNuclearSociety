from django.shortcuts import render
from django.http import HttpResponse


def main(request):
    return render(request, 'main/base.html')

def registration(request):
    return render(request, 'main/register.html')

def login(request):
    return render(request, 'main/login.html')

def logout(request):
    return None
