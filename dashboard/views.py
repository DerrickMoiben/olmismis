from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from .forms import SignupForm, LoginForm, FarmerForm, FarmerWeightForm
from django.contrib.auth.models import User
from .models import Farmer
from django.core.exceptions import MultipleObjectsReturned
import logging
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_protect

logger = logging.getLogger(__name__)


def land_page(request):
    return render(request, 'index.html')
def dashboard(request):
    return render(request, 'registration/dashboard.html')

def user_signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = SignupForm()
    return render(request, 'registration/signup.html', {'form': form})

@csrf_protect
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            logger.info(f"Username: {username}, Password: {password}, User: {user}")
            if user:
                login(request, user)
                return redirect('admin-dashboard')
            else:
                logger.error("Authentication failed")
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('login')

def admin_dashboard(request):
    if request.method == 'POST':
       form = FarmerWeightForm(request.POST)
       if form.is_valid():
            farmer_name = form.cleaned_data.get('Farmer')
            berry_weight = form.cleaned_data.get('berry_weight')
            try:
                farmer = Farmer.objects.get(name=farmer_name)
                farmer.berry_weight = berry_weight
            except Farmer.DoesNotExist:
                farmer = Farmer(name=farmer_name, berry_weight=berry_weight)
            except MultipleObjectsReturned:
                # If multiple farmers with the same name are found,
                # handle the situation appropriately, such as logging an error
                # or selecting one of the farmers to use
                # For now, let's just log the error
                print("Multiple farmers with the same name:", farmer_name)
            farmer.save()
            return redirect('admin-dashboard')
    else:
        form = FarmerWeightForm()
    return render(request, 'admin/admin_dashboard.html', {'form': form})
def register_new_farmer(request):
    if request.method == 'POST':
        form = FarmerForm(request.POST)
        if form.is_valid():
            farmer = form.save(commit=False)
            farmer_name = form.cleaned_data.get('name')
            farmer.save()
            return redirect('admin-dashboard')
        
    else:
        form = FarmerForm
    return render(request, 'admin/register_farmer.html', {'form': form})
def all_farmers(request):
    farmers = Farmer.objects.all()
    return render(request, 'admin/all_farmers.html', {'farmers': farmers})