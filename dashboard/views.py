from django.shortcuts import render, redirect
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

#@csrf_protect
#def admin_dashboard(request):
    farmer_id = request.GET.get('farmer_id')  # Get farmer ID from URL parameter

    if request.method == 'POST':
        form = FarmerWeightForm(request.POST)
        if form.is_valid():
            farmer_name = form.cleaned_data.get('farmer_name')
            berry_weight = form.cleaned_data.get('berry_weight')

            # ... existing logic for weight submission ...

            if farmer_id:
                farmer = Farmer.objects.get(pk=farmer_id)  # Retrieve farmer by ID
                farmer.berry_weight = berry_weight
                farmer.save()
    else:
        if farmer_id:
            try:
                farmer = Farmer.objects.get(pk=farmer_id)  # Pre-fill form with farmer data
                form = FarmerWeightForm(initial={'farmer_name': farmer.name})  # Set initial farmer name
            except Farmer.DoesNotExist:
                logger.error(f"Farmer with ID {farmer_id} not found.")
                return render(request, 'admin/admin_dashboard.html', {'form': form, 'error': 'Farmer not found.'})
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

#def register_new_farmer(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            #farmer = form.save(commit=False)
            farmer = form.save()
            return redirect('admin-dashboard', farmer_id=farmer.id) # Redirect to the admin dashboard with id 
    else:
        form = RegisterForm()
    return render(request, 'admin/register_farmer.html', {'form': form})


def all_farmers(request):
    farmers = Farmer.objects.all()
    logger.debug(f"Retrieved farmers: {farmers}")
    return render(request, 'admin/all_farmers.html', {'farmers': farmers})

#@csrf_protect
#@transaction.atomic
#def register_new_farmer(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            farmer = form.save()
            return redirect('admin-dashboard', farmer_id=farmer.id)
    else:
        form = RegisterForm()
    return render(request, 'admin/register_farmer.html', {'form': form})

#@csrf_protect
#@transaction.atomic
#def admin_dashboard(request):
    farmer_id = request.GET.get('farmer_id')

    if request.method == 'POST':
        form = FarmerWeightForm(request.POST)
        if form.is_valid():
            farmer_name = form.cleaned_data.get('farmer_name')
            berry_weight = form.cleaned_data.get('berry_weight')

            try:
                farmer = Farmer.objects.get(name=farmer_name)
            except Farmer.DoesNotExist:
                logger.error(f"Farmer {farmer_name} not found.")
                return render(request, 'admin/admin_dashboard.html', {'form': form, 'error': 'Farmer not found.'})

            farmer.berry_weight = berry_weight
            farmer.save()
            return redirect('admin-dashboard')
    else:
        if farmer_id:
            try:
                farmer = Farmer.objects.get(pk=farmer_id)
                form = FarmerWeightForm(initial={'farmer_name': farmer.name})
            except Farmer.DoesNotExist:
                logger.error(f"Farmer with ID {farmer_id} not found.")
                return render(request, 'admin/admin_dashboard.html', {'form': form, 'error': 'Farmer not found.'})
        else:
            form = FarmerWeightForm()
    return render(request, 'admin/admin_dashboard.html', {'form': form})

def register_new_farmer(request):
    if request.method == 'POST':
        form = FarmerForm(request.POST)
        if form.is_valid():
            farmer = form.save(commit=False)
            farmer.id_number =  str(Farmer.objects.count() + 1)
            farmer.save()
            messages.success(request, 'Farmer registered successfully.')
            return redirect('enter-weight', farmer_id=farmer.id)
    else:
        form = FarmerForm()
    return render(request, 'admin/register_farmer.html', {'form': form})


#def enter_weight(request, farmer_id):
    farmer = Farmer.objects.get(id=farmer_id)

    try:
        field = Field.objects.get(farmer=farmer)
    except Field.DoesNotExist:
        field =Field.objects.create(farmer=farmer, field_name="Default Field Name")
    total_coffee_weight = CoffeeBerries.objects.filter(field=field).aggregate(Sum('weight'))['weight__sum'] or 0

    if request.method == 'POST':
        form = CoffeeBerriesForm(request.POST)
        if form.is_valid():
            coffee_berrie = form.save(commit=False)
            coffee_berrie.field = field
            coffee_berrie.save()
            messages.success(request, 'Coffee berries weight added successfully.')
            return redirect('admin-dashboard')
    else:
        form = CoffeeBerriesForm()
    return render(request, 'admin/coffee_weight.html', {'farmer': farmer, 'field': field, 'total_coffee_weight': total_coffee_weight, 'form': form})

#def admin_dashboard(request):
    farmers = Farmer.objects.all()

    if request.method == 'POST':
        form = CoffeeBerriesForm(request.POST)
        if form.is_valid():
            farmer_name = form.cleaned_data.get('farmer_name')
            weight = form.cleaned_data.get('weight')

            try:
                farmer = Farmer.objects.get(name=farmer_name)
                field, created = Field.objects.get_or_create(farmer=farmer, field_name="Default Field Name")
                coffee_berrie, created = CoffeeBerries.objects.get_or_create(field=field)
                coffee_berrie.weight = weight
                coffee_berrie.save()
                return redirect('admin-dashboard')
            except Farmer.DoesNotExist:
                logger.error(f"Farmer with name {farmer_name} not found.")
                return render(request, 'admin/admin_dashboard.html', {'farmers': farmers, 'form': form, 'error': 'Farmer not found.'})
        
    else:
        form = CoffeeBerriesForm()
        return render(request, 'admin/admin_dashboard.html', {'farmers': farmers, 'form': form})

#def enter_weight(request, farmer_id):
    farmer = Farmer.objects.get(id=farmer_id)

    try:
        field = Field.objects.get(farmer=farmer)
    except Field.DoesNotExist:
        field = Field.objects.create(farmer=farmer, field_name="Default Field Name")
    total_coffee_weight = CoffeeBerries.objects.filter(field=field).aggregate(Sum('weight'))['weight__sum'] or 0

    if request.method == 'POST':
        form = CoffeeBerriesForm(request.POST)
        if form.is_valid():
            weight = form.cleaned_data['weight']
            coffee_berrie, created = CoffeeBerries.objects.get_or_create(field=field)
            coffee_berrie.weight = weight
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
            
            try:
                farmer = Farmer.objects.filter(name=farmer_name).first()  # Use filter() instead of get()
                if farmer:
                    field, created = Field.objects.get_or_create(farmer=farmer, field_name="Default Field Name")
                    coffee_berrie, created = CoffeeBerries.objects.get_or_create(field=field)
                    coffee_berrie.weight = weight
                    coffee_berrie.save()
                    return redirect('admin-dashboard')  # Redirect to a success page
                else:
                    messages.error(request, 'Farmer not found. Please enter a valid farmer name.')
            except Farmer.DoesNotExist:
                messages.error(request, 'Farmer not found. Please enter a valid farmer name.')
    else:
        form = CoffeeBerriesForm()
    
    return render(request, 'admin/admin_dashboard.html', {'farmers': farmers, 'form': form})

#def admin_dashboard(request):
    farmers = Farmer.objects.all()
    
    if request.method == 'POST':
        form = CoffeeBerriesForm(request.POST)
        if form.is_valid():
            farmer_name = form.cleaned_data['farmer_name']
            weight = form.cleaned_data['weight']
            
            try:
                farmer = Farmer.objects.filter(name=farmer_name).first()
                if farmer:
                    field, created = Field.objects.get_or_create(farmer=farmer, field_name="Default Field Name")
                    coffee_berrie, created = CoffeeBerries.objects.get_or_create(field=field)
                    coffee_berrie.weight = weight
                    coffee_berrie.save()
                    return redirect('admin-dashboard')  # Redirect to a success page
                else:
                    messages.error(request, 'Farmer not found. Please enter a valid farmer name.')
            except Farmer.DoesNotExist:
                messages.error(request, 'Farmer not found. Please enter a valid farmer name.')
    else:
        form = CoffeeBerriesForm()
    
    return render(request, 'admin/admin_dashboard.html', {'farmers': farmers, 'form': form})

def enter_weight(request, farmer_id):
    farmer = Farmer.objects.get(id=farmer_id)

    try:
        field = Field.objects.get(farmer=farmer)
    except Field.DoesNotExist:
        field = Field.objects.create(farmer=farmer, field_name="Default Field Name")
    total_coffee_weight = CoffeeBerries.objects.filter(field=field).aggregate(Sum('weight'))['weight__sum'] or 0

    if request.method == 'POST':
        form = CoffeeBerriesForm(request.POST)
        if request.method == 'POST':
            form = CoffeeBerriesForm(request.POST)
            if form.is_valid():
                weight = form.cleaned_data['weight']
                coffee_berrie, created = CoffeeBerries.objects.get_or_create(field=field, defaults={'weight': weight})
                if not created:
                        coffee_berrie.weight = weight  # Update weight only if the object already exists
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

def admin_dashboard(request):
    farmers = Farmer.objects.all()
    
    if request.method == 'POST':
        form = CoffeeBerriesForm(request.POST)
        if form.is_valid():
            farmer_name = form.cleaned_data['farmer_name']
            weight = form.cleaned_data['weight']
            
            try:
                farmer = Farmer.objects.filter(name=farmer_name).first()
                if farmer:
                    field, created = Field.objects.get_or_create(farmer=farmer, field_name="Default Field Name")
                    coffee_berrie, created = CoffeeBerries.objects.get_or_create(field=field)
                    coffee_berrie.weight = weight
                    coffee_berrie.save()
                    return redirect('admin-dashboard')  # Redirect to a success page
                else:
                    messages.error(request, 'Farmer not found. Please enter a valid farmer name.')
            except Farmer.DoesNotExist:
                messages.error(request, 'Farmer not found. Please enter a valid farmer name.')
    else:
        form = CoffeeBerriesForm()
    
    return render(request, 'admin/admin_dashboard.html', {'farmers': farmers, 'form': form})
