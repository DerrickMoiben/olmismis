from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from .forms import SignupForm, LoginForm,  FarmerForm, CoffeeBerriesForm
from django.contrib.auth.models import User
from .models import Farmer, Field, CoffeeBerries
from django.core.exceptions import MultipleObjectsReturned
import logging
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum

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

def register_new_farmer(request):
    if request.method == 'POST':
        form = FarmerForm(request.POST)
        if form.is_valid():
            farmer = form.save(commit=False)
            farmer.id_number = str(Farmer.objects.count() + 1)
            farmer.save()
            messages.success(request, 'Farmer registered successfully.')
            return redirect('enter-weight', farmer_id=farmer.id)
        else:
            messages.error(request, '')
    else:
        form = FarmerForm()
    return render(request, 'admin/register_farmer.html', {'form': form})

#def enter_weight(request, farmer_id):
    farmer = get_object_or_404(Farmer, id=farmer_id)
    
    try:
        field = Field.objects.get(farmer=farmer)
    except Field.DoesNotExist:
        field = Field.objects.create(farmer=farmer, field_name="Default Field Name")
    
    total_coffee_weight = CoffeeBerries.objects.filter(field=field).aggregate(Sum('weight'))['weight__sum'] or 0

    if request.method == 'POST':
        form = CoffeeBerriesForm(request.POST)
        if form.is_valid():
            coffee_berrie, created = CoffeeBerries.objects.get_or_create(field=field, defaults={'weight': form.cleaned_data['weight']})
            if not created:
                coffee_berrie.weight = form.cleaned_data['weight']  # Update weight if it already exists
                coffee_berrie.save()
            messages.success(request, 'Coffee berries weight added successfully.')
            return redirect('admin-dashboard')
    else:
        form = CoffeeBerriesForm()

    return render(request, 'admin/coffee_weight.html', {
        'farmer': farmer,
        'field': field,
        'total_coffee_weight': total_coffee_weight,
        'form': form
    })
  

#def admin_dashboard(request):
    farmers = Farmer.objects.all()
    
    if request.method == 'POST':
        form = CoffeeBerriesForm(request.POST)
        if form.is_valid():
            farmer_name = form.cleaned_data['farmer_name']
            weight = form.cleaned_data['weight']
            
            farmer = Farmer.objects.filter(name=farmer_name).first()
            if farmer:
                try:
                    field = Field.objects.get(farmer=farmer, field_name="Default Field Name")
                except Field.DoesNotExist:
                    field = Field.objects.create(farmer=farmer, field_name="Default Field Name")
                
                coffee_berrie, created = CoffeeBerries.objects.get_or_create(field=field, defaults={'weight': weight})
                if not created:
                    coffee_berrie.weight = weight
                    coffee_berrie.save()
                messages.success(request, 'Coffee berries weight updated successfully.')
                return redirect('admin-dashboard')
            else:
                messages.error(request, 'Farmer not found. Please enter a valid farmer name.')
    else:
        form = CoffeeBerriesForm()

    return render(request, 'admin/admin_dashboard.html', {'farmers': farmers, 'form': form})
def enter_weight(request, farmer_id):
    farmer = get_object_or_404(Farmer, id=farmer_id)
    
    try:
        field = Field.objects.get(farmer=farmer)
    except Field.DoesNotExist:
        field = Field.objects.create(farmer=farmer, field_name="Default Field Name")
    
    total_coffee_weight = CoffeeBerries.objects.filter(field=field).aggregate(Sum('weight'))['weight__sum'] or 0

    if request.method == 'POST':
        form = CoffeeBerriesForm(request.POST)
        if form.is_valid():
            weight = form.cleaned_data['weight']
            coffee_berrie, created = CoffeeBerries.objects.get_or_create(field=field, defaults={'weight': weight})
            if not created:
                coffee_berrie.weight += weight  # Add the new weight to the existing weight
                coffee_berrie.save()
            else:
                total_coffee_weight += weight  # Update the total weight if new entry is created
            messages.success(request, 'Coffee berries weight added successfully.')
            return redirect('enter-weight', farmer_id=farmer.id)
    else:
        form = CoffeeBerriesForm()

    return render(request, 'admin/coffee_weight.html', {
        'farmer': farmer,
        'field': field,
        'total_coffee_weight': total_coffee_weight,
        'form': form
    })
def admin_dashboard(request):
    farmers = Farmer.objects.all()
    
    if request.method == 'POST':
        form = CoffeeBerriesForm(request.POST)
        if form.is_valid():
            farmer_name = form.cleaned_data['farmer_name']
            weight = form.cleaned_data['weight']
            
            farmer = Farmer.objects.filter(name=farmer_name).first()
            if farmer:
                try:
                    field = Field.objects.get(farmer=farmer, field_name="Default Field Name")
                except Field.DoesNotExist:
                    field = Field.objects.create(farmer=farmer, field_name="Default Field Name")
                
                coffee_berrie, created = CoffeeBerries.objects.get_or_create(field=field, defaults={'weight': weight})
                if not created:
                    coffee_berrie.weight += weight  # Add the new weight to the existing weight
                    coffee_berrie.save()
                messages.success(request, 'Coffee berries weight updated successfully.')
                return redirect('admin-dashboard')
            else:
                messages.error(request, 'Farmer not found. Please enter a valid farmer name.')
    else:
        form = CoffeeBerriesForm()

    # Calculate total coffee weight for each farmer
    for farmer in farmers:
        fields = Field.objects.filter(farmer=farmer)
        total_weight = CoffeeBerries.objects.filter(field__in=fields).aggregate(Sum('weight'))['weight__sum'] or 0
        farmer.total_coffee_weight = total_weight

    return render(request, 'admin/admin_dashboard.html', {'farmers': farmers, 'form': form})


def all_farmers(request):
    farmers = Farmer.objects.all()
    total_coffee_weight = 0
    for farmer in farmers:
        farmer_fields = farmer.field_set.all()
        farmer_coffee_weight = sum(coffee.weight for coffee in CoffeeBerries.objects.filter(field__in=farmer_fields))
        farmer.coffee_weight = farmer_coffee_weight
        total_coffee_weight += farmer_coffee_weight

    context = {
        'farmers': farmers,
        'total_coffee_weight': total_coffee_weight,
    }
    return render(request, 'admin/all_farmers.html', context)

def delete_farmer(request, farmer_id):
    farmer = get_object_or_404(Farmer, id=farmer_id)
    farmer.delete()
    messages.success(request, 'Farmer deleted successfully.')
    return redirect('all-farmers')