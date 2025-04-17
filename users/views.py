from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from recommendations.gorse_client import GorseClient

def login_view(request):
    """Handle user login"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                return redirect('core:home')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'users/login.html', {'form': form})

def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('core:home')

def register_view(request):
    """Handle user registration"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            login(request, user)
            messages.success(request, f"Account created for {username}!")
            return redirect('core:home')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = UserCreationForm()
    
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile_view(request):
    """Display and update user profile"""
    return render(request, 'users/profile.html')

@login_required
def orders_view(request):
    """Display user's order history"""
    # In a real app, you would retrieve orders from a database
    # For now, we'll just render an empty orders page
    return render(request, 'users/orders.html')

@login_required
def checkout_view(request):
    """Handle checkout process"""
    # This would typically include shipping, payment, etc.
    return render(request, 'users/checkout.html')