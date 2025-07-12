from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render
from django.urls import reverse

def dashboard(request):
    return render(request, "users/dashboard.html")

