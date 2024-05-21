from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from .forms import SignupForm, LoginForm, RegisterForm, FarmerWeightForm
from django.contrib.auth.models import User
from .models import Farmer
from django.core.exceptions import MultipleObjectsReturned
import logging
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages

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

#@csrf_protect
#def admin_dashboard(request):
    if request.method == 'POST':
        form = FarmerWeightForm(request.POST)
        if form.is_valid():
            farmer_name = form.cleaned_data.get('Farmer')
            berry_weight = form.cleaned_data.get('berry_weight')
            #retrieve the farmer instance
            try:
                farmer = Farmer.objects.get(name=farmer_name)
            except Farmer.DoesNotExist:
                form.add_error('Farmer', 'Farmer does not exist')
                logger.error(f"Farmer {farmer_name} does not exist")
                return render(request, 'admin/admin_dashboard.html', {'form': form})

            #update the farmer berry weight and save
            farmer.berry_weight = berry_weight
            farmer.save()
            Farmer.objects.all().refresh_from_db() # Refresh the database
            return redirect('admin-dashboard')
    else:
        form = FarmerWeightForm()
    return render(request, 'admin/admin_dashboard.html', {'form': form})
#@csrf_protect
#def admin_dashboard(request):
    if request.method == 'POST':
        form = FarmerWeightForm(request.POST)
        if form.is_valid():
            farmer_name = form.cleaned_data.get('farmer_name')
            berry_weight = form.cleaned_data.get('berry_weight')
            farmer, created = Farmer.objects.get_or_create(name=farmer_name)
            #retrieve the farmer instance
            if created:
                logger.info(f"New farmer {farmer_name} created")
            #update the farmer berry weight and save
            farmer.berry_weight = berry_weight
            farmer.save()
            farmer.objects.all().refresh_from_db()
            return redirect('admin-dashboard')
    else:
        form = FarmerWeightForm()
    return render(request, 'admin/admin_dashboard.html', {'form': form})

@csrf_protect
def admin_dashboard(request):
    if request.method == 'POST':
        form = FarmerWeightForm(request.POST)
        if form.is_valid():
            farmer_name = form.cleaned_data.get('farmer_name')
            berry_weight = form.cleaned_data.get('berry_weight')
            
            # Log the values to debug
            logger.debug(f"Farmer name: {farmer_name}, Berry weight: {berry_weight}")

            if not farmer_name:
                logger.error("Farmer name is missing or invalid.")
                return render(request, 'admin/admin_dashboard.html', {'form': form, 'error': 'Farmer name is required.'})

            farmer, created = Farmer.objects.get_or_create(name=farmer_name)
            if created:
                logger.info(f"New farmer {farmer_name} created")
            farmer.berry_weight = berry_weight
            farmer.save()
            return redirect('admin-dashboard')
    else:
        form = FarmerWeightForm()
    return render(request, 'admin/admin_dashboard.html', {'form': form})

def register_new_farmer(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            farmer = form.save(commit=False)
            form.save()
            return redirect('admin-dashboard')
    else:
        form = RegisterForm()
    return render(request, 'admin/register_farmer.html', {'form': form})

def all_farmers(request):
    farmers = Farmer.objects.all()
    return render(request, 'admin/all_farmers.html', {'farmers': farmers})

