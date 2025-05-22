from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login, authenticate, logout as auth_logout
from django.contrib import messages
from .models import User
from .forms import UserForm, SigninForm

def signup(request):
    if request.user.is_authenticated:
        # Redirect to home page if user is already logged in
        return redirect('home')

    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            form.save() # Password is already hashed in the form
            return redirect(request.GET.get('next', 'signin'))
    else:
        form = UserForm()

    context = {
        'form': form,
        'title': 'Join OWLPHA UNIVERSITY — Explore Free Web3 Courses & Community',
    }

    return render(request, 'pages/signup.html', context)

def signin(request):
    if request.user.is_authenticated:
        # Redirect to home page if user is already logged in
        return redirect('home')

    if request.method == 'POST':
        form = SigninForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['identifier']
            password = form.cleaned_data['password']

            # Try authenticating by username or email
            user = authenticate(request, username=identifier, password=password)

            if user:
                auth_login(request, user)
                return redirect(request.GET.get('next', 'home'))
            else:
                messages.error(request, "Invalid credentials. Please check and try again.")

    else:
        form = SigninForm()

    context = {
        'form': form,
        'title': 'Access Your OWLPHA UNIVERSITY Account | Learn Web3 & Blockchain',
    }

    return render(request, 'pages/signin.html', context)

# Handles user logout while keeping session data intact.
def logout(request):
    auth_logout(request)
    return redirect('home')

def home(request):
    context = {
        'title' : 'Hello',
    }
    return render(request, 'pages/dashboard.html', context)
