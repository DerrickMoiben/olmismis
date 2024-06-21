from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from .forms import SignupForm, LoginForm,  FarmerForm, CoffeeBerriesForm
from .models import Farmer, Field, CoffeeBerries
import logging
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.db.models import Sum
from datetime import datetime
from apis.sms import send_sms
from escpos.printer import Usb
import json

logger = logging.getLogger(__name__)


def land_page(request):
    return render(request, 'index.html')

@csrf_protect
def cashier_signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cashier-login')
    else:
        form = SignupForm()
    return render(request, 'registration/signup.html', {'form': form})

@csrf_protect
def cashier_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            cashier = authenticate(username=username, password=password)
            logger.info(f"Username: {username}, Password: {password}, User: {cashier}")
            if cashier:
                login(request, cashier)
                return redirect('cashier-dashboard')
            else:
                logger.error("Authentication failed")
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})


# @csrf_protect
# def register_new_farmer(request):
#     if request.method == 'POST':
#         form = FarmerForm(request.POST)
#         if form.is_valid():
#             farmer = form.save(commit=False)
#             farmer.number = str(Farmer.objects.count() + 1)
#             farmer.save()
#             messages.success(request, 'Farmer registered successfully.')
#             #send sms
#             send_sms(f"Dear {farmer.name}, you have been registered successfully at OLMISMIS FCS Ltd. Your  number is {farmer.number}.", [farmer.phone])
#             return redirect('enter-weight', farmer_id=farmer.id)
#         else:
#             messages.error(request, '')
#     else:
#         form = FarmerForm()
#     return render(request, 'admin/register_farmer.html', {'form': form})

@csrf_protect
def register_new_farmer(request):
    if request.method == 'POST':
        form = FarmerForm(request.POST)
        if form.is_valid():
            farmer = form.save(commit=False)
            farmer.number = f'{Farmer.objects.count() + 1:03}'
            farmer.save()
            messages.success(request, 'Farmer registered successfully.')
            try:
                send_sms(f"Dear {farmer.name}, you have been registered successfully at OLMISMIS FCS Ltd. Your number is {farmer.number}.", [farmer.phone])
            except Exception as e:
                messages.warning(request, f'Failed to send SMS: {e}')
            return redirect('cashier-dashboard')
        else:
            # Form is not valid, display user-friendly error messages
            error_messages = '\n'.join([f"{error}" for field, error in form.errors.items()])
            messages.error(request, f'Failed to register farmer. Errors:\n{error_messages}')
            return render(request, 'admin/register_farmer.html', {'form': form})
    else:
        form = FarmerForm()
    
    return render(request, 'admin/register_farmer.html', {'form': form})



#@csrf_protect
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
            weight = form.cleaned_data['weight']
            coffee_berrie, created = CoffeeBerries.objects.get_or_create(field=field, defaults={'weight': weight})

            if not created:
                coffee_berrie.weight += weight  # Add the new weight to the existing weight
                coffee_berrie.save()
            else:
                total_coffee_weight += weight  # Update the total weight if new entry is created
                
                #send sms
                try:
                    current_datetime = datetime.now()
                    formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M')

                    #send_sms(f"Dear {farmer.name}, on {formatted_datetime}  you weighed {weight} kgs of coffee berries . Your total coffee weight is {total_coffee_weight} kgs.", [farmer.phone])
                except Exception as e:  
                    logger.error(f"Error sending SMS: {e}")
                    messages.error(request, f'Error sending SMS: {e}')
                    
                messages.success(request, 'SMS sent successfully.and coffee weight added successfully.')

            return redirect('enter-weight', farmer_id=farmer.id)
        messages.error(request, 'Please enter a valid weight.')
        messages.success(request, 'Coffee berries weight added successfully.')
    else:
        form = CoffeeBerriesForm()

    return render(request, 'admin/coffee_weight.html', {
        'farmer': farmer,
        'field': field,
        'total_coffee_weight': total_coffee_weight,
        'form': form
    })

@csrf_protect
def cashier_dashboard(request):
    farmers = Farmer.objects.all()
    
    if request.method == 'POST':
        form = CoffeeBerriesForm(request.POST)
        if form.is_valid():
            farmer_number = form.cleaned_data['farmer_number']
            weight = form.cleaned_data['weight']
            
            farmer = Farmer.objects.filter(number=farmer_number).first()
            if farmer:
                phone_number = farmer.phone
                try:
                    field = Field.objects.get(farmer=farmer, field_name="Default Field Name")
                except Field.DoesNotExist:
                    field = Field.objects.create(farmer=farmer, field_name="Default Field Name")
                
                coffee_berrie, created = CoffeeBerries.objects.get_or_create(field=field, defaults={'weight': weight})
                if not created:
                    coffee_berrie.weight += weight  # Add the new weight to the existing weight
                    coffee_berrie.save()
                    
                # Calculate total coffee weight for the updated farmer
                farmer_fields = Field.objects.filter(farmer=farmer)
                farmer_total_weight = CoffeeBerries.objects.filter(field__in=farmer_fields).aggregate(Sum('weight'))['weight__sum'] or 0
                farmer.total_coffee_weight = farmer_total_weight
                farmer.save()

                try:
                    current_datetime = datetime.now()
                    formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M')
                    time = current_datetime.strftime('%H:%M')
                    date = current_datetime.date()

                    #Uncomment the SMS sending code if you want to use it
                    try:                    
                        send_sms(f"Dear {farmer.name}, on {formatted_datetime} you weighed {weight} kgs of coffee berries. Your total coffee weight is {farmer_total_weight} kgs.", [phone_number])
                    except Exception as e:
                        logger.error(f"Error sending SMS: {e}")
                        messages.error(request, f'Error sending SMS: {e}')
                    
                    # Print the receipt
                    printer = Usb(0x0fe6, 0x811e, in_ep=0x82, out_ep=0x01)
                    printer.set(align='center', font='b', width=4, height=6)
                    printer.text("========================================\n")
                    printer.text("OLMISMIS FCS Ltd\n")
                    printer.text("========================================\n")
                    printer.text(f"Date: {date}\n")
                    printer.text(f"Time: {time}\n")
                    printer.text("========================================\n")
                    printer.text(f"Farmer Name: {farmer.name}\n")
                    printer.text(f"Farmer number: {farmer.number}\n")
                    printer.text(f"Weight of the Day: {weight} kgs\n")
                    printer.text(f"Total Coffee Weight: {farmer_total_weight} kgs\n")
                    printer.text("========================================\n\n\n")
                    printer.cut()

                except Exception as e:
                    logger.error(f"Error sending SMS: {e}")
                    messages.error(request, f'Error sending SMS: {e}')
                messages.success(request, 'Coffee berries weight updated successfully.')
                return redirect('cashier-dashboard')
            else:
                messages.error(request, 'Farmer not found. Please enter a valid farmer number.')
    else:
        form = CoffeeBerriesForm()

    return render(request, 'admin/admin_dashboard.html', {'farmers': farmers, 'form': form})


@csrf_protect
def cashier_farmers(request):
    search_farmer = request.GET.get('search', '')
    if search_farmer:
        farmers = Farmer.objects.filter(name__icontains=search_farmer)
    else:
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
        'search_query': search_farmer,
    }
    return render(request, 'admin/cashier_farmers.html', context)
