from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from .forms import AnnouncementsForm, SignupForm, LoginForm,  FarmerForm, CoffeeBerriesForm
from .models import Farmer, Field, CoffeeBerries
import logging
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.db.models import Sum
from datetime import datetime
from escpos.printer import Usb
import json
import win32print
import win32api
from django.conf import settings
from apis.sms import send_sms

logger = logging.getLogger(__name__)


def land_page(request):
    return render(request, 'index.html')

@csrf_protect
def user_signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sign up successfully')
            return redirect('login')
        else:
            messages.error('Sign up was unseccefull')
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



@csrf_protect
def register_new_farmer(request):
    if request.method == 'POST':
        form = FarmerForm(request.POST)
        if form.is_valid():
            farmer = form.save(commit=False)
            farmer.number = f'{Farmer.objects.count() + 1:03}'
            phone = form.cleaned_data.get('phone')
            f_phone = '+254'
            f_phone += phone
            farmer.phone = f_phone
            farmer.save()
            messages.success(request, 'Farmer registered successfully.')
            try:
                send_sms(f"Dear {farmer.name}, you have been registered successfully at OLMISMIS Dairy FCS Ltd. Your number is {farmer.number}.", [farmer.phone])
            except Exception as e:
                messages.warning(request, f'Failed to send SMS: {e}')
            return render(request, 'admin/register_farmer.html')
        else:
            # Form is not valid, display user-friendly error messages
            error_messages = '\n'.join([f"{error}" for field, error in form.errors.items()])
            messages.error(request, f'Failed to register farmer. Errors:\n{error_messages}')
            return render(request, 'admin/register_farmer.html', {'form': form})
    else:
        form = FarmerForm()
    
    return render(request, 'admin/register_farmer.html', {'form': form})

@csrf_protect
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
                
                #send sms
                try:
                    current_datetime = datetime.now()
                    formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M')

                    send_sms(f"Dear {farmer.name}, on {formatted_datetime}  you weighed {weight} kgs of Milk . Your total Milk weight is {total_coffee_weight} kgs.", [farmer.phone])
                    print('sms sent')
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
@csrf_protect
def delete_farmer(request, farmer_id):
    farmer = get_object_or_404(Farmer, id=farmer_id)
    farmer.delete()
    messages.success(request, 'Farmer deleted successfully.')
    return redirect('all-farmers')


# @csrf_protect
# def admin_dashboard(request):
#     farmers = Farmer.objects.all()
    
#     if request.method == 'POST':
#         form = CoffeeBerriesForm(request.POST)
#         if form.is_valid():
#             farmer_name = form.cleaned_data['farmer_name']
#             weight = form.cleaned_data['weight']
            
#             farmer = Farmer.objects.filter(name=farmer_name).first()
#             if farmer:
#                 try:
#                     field = Field.objects.get(farmer=farmer, field_name="Default Field Name")
#                 except Field.DoesNotExist:
#                     field = Field.objects.create(farmer=farmer, field_name="Default Field Name")
                
#                 coffee_berrie, created = CoffeeBerries.objects.get_or_create(field=field, defaults={'weight': weight})
#                 if not created:
#                     coffee_berrie.weight += weight  # Add the new weight to the existing weight
#                     coffee_berrie.save()
                    
#                 # Calculate total coffee weight for the updated farmer
#                 farmer_fields = Field.objects.filter(farmer=farmer)
#                 farmer_total_weight = CoffeeBerries.objects.filter(field__in=farmer_fields).aggregate(Sum('weight'))['weight__sum'] or 0
#                 farmer.total_coffee_weight = farmer_total_weight
#                 farmer.save()

#                 try:
#                     current_datetime = datetime.now()
#                     formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M')
#                     time = current_datetime.strftime('%H:%M')
#                     date = current_datetime.date()

#                     # Construct the receipt content
#                     content = "========================================\n"
#                     content += "OLMISMIS FCS Ltd\n"
#                     content += "========================================\n"
#                     content += f"Date: {date}\n"
#                     content += f"Time: {time}\n"
#                     content += "========================================\n"
#                     content += f"Farmer Name: {farmer.name}\n"
#                     content += f"Farmer number: {farmer.number}\n"
#                     content += f"Weight of the Day: {weight} kgs\n"
#                     content += f"Total Coffee Weight: {farmer_total_weight} kgs\n"
#                     content += "========================================\n\n\n"

#                     # ESC/POS command to cut the paper
#                     cut_paper = "\x1d\x56\x41\x10"  # Full cut
#                     full_content = content + cut_paper

#                     # Set the printer name
#                     printer_name = "POS Printer 80250 Series"

#                     # Open the printer and start a document
#                     printer_handle = win32print.OpenPrinter(printer_name)
#                     job_handle = win32print.StartDocPrinter(printer_handle, 1, ("Receipt", None, "RAW"))
#                     win32print.StartPagePrinter(printer_handle)

#                     # Write the content to the printer
#                     win32print.WritePrinter(printer_handle, full_content.encode('utf-8'))

#                     # End the page and document, then close the printer
#                     win32print.EndPagePrinter(printer_handle)
#                     win32print.EndDocPrinter(printer_handle)
#                     win32print.ClosePrinter(printer_handle)

#                 except Exception as e:
#                     logger.error(f"Error printing receipt: {e}")
#                     messages.error(request, f'Error printing receipt: {e}')
#                 messages.success(request, 'Coffee berries weight updated successfully.')
#                 return redirect('admin-dashboard')
#             else:
#                 messages.error(request, 'Farmer not found. Please enter a valid farmer name.')
#     else:
#         form = CoffeeBerriesForm()

#     return render(request, 'admin/admin_dashboard.html', {'farmers': farmers, 'form': form})



@csrf_protect
def admin_dashboard(request):
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
                        send_sms(f"Dear {farmer.name}, on {formatted_datetime} you weighed {weight} kgs of milk. Your total milk weight is {farmer_total_weight} kgs.", [phone_number])
                    except Exception as e:
                        logger.error(f"Error sending SMS: {e}")
                        messages.error(request, f'Error sending SMS: {e}')
                    
                    # Construct the receipt content
                    content = "========================================\n"
                    content += "OLMISMIS FCS Ltd\n"
                    content += "========================================\n"
                    content += f"Date: {date}\n"
                    content += f"Time: {time}\n"
                    content += "========================================\n"
                    content += f"Farmer Name: {farmer.name}\n"
                    content += f"Farmer number: {farmer.number}\n"
                    content += f"Weight of the Day: {weight} kgs\n"
                    content += f"Total Milk Weight: {farmer_total_weight} kgs\n"
                    content += "========================================\n\n\n"

                    # ESC/POS command to cut the paper
                    cut_paper = "\x1d\x56\x41\x10"  # Full cut
                    full_content = content + cut_paper

                    # Set the printer name
                    printer_name = "POS Printer 80250 Series"

                    # Open the printer and start a document
                    printer_handle = win32print.OpenPrinter(printer_name)
                    job_handle = win32print.StartDocPrinter(printer_handle, 1, ("Receipt", None, "RAW"))
                    win32print.StartPagePrinter(printer_handle)

                    # Write the content to the printer
                    win32print.WritePrinter(printer_handle, full_content.encode('utf-8'))

                    # End the page and document, then close the printer
                    win32print.EndPagePrinter(printer_handle)
                    win32print.EndDocPrinter(printer_handle)
                    win32print.ClosePrinter(printer_handle)

                except Exception as e:
                    logger.error(f"Error printing receipt: {e}")
                    messages.error(request, f'Error printing receipt: {e}')
                messages.success(request, 'Coffee berries weight updated successfully.')
                return redirect('admin-dashboard')
            else:
                messages.error(request, 'Farmer not found. Please enter a valid farmer number.')
    else:
        form = CoffeeBerriesForm()

    return render(request, 'admin/admin_dashboard.html', {'farmers': farmers, 'form': form})


@csrf_protect
def print_farmer_report(request):
    try:
        farmers = Farmer.objects.all()
        total_coffee_weight = 0

        # Calculate coffee weights for each farmer
        for farmer in farmers:
            farmer_fields = farmer.field_set.all()
            farmer_coffee_weight = sum(coffee.weight for coffee in CoffeeBerries.objects.filter(field__in=farmer_fields))
            farmer.coffee_weight = farmer_coffee_weight
            total_coffee_weight += farmer_coffee_weight

        # Prepare context for rendering
        context = {
            'farmers': farmers,
            'total_coffee_weight': total_coffee_weight,
        }

        # Set the printer name
        printer_name = "EPSON L3250 Series"

        # Construct the content to be printed
        content = "========================================\n"
        content += "OLMISMIS FCS Ltd\n"
        content += "========================================\n"
        content += "Farmers Report\n"
        content += "========================================\n"
        for farmer in farmers:
            content += f"Farmer Name: {farmer.name}\n"
            content += f"Farmer Number: {farmer.number}\n"
            content += f"Total Coffee Weight: {farmer.coffee_weight} kgs\n"
            content += "========================================\n"
        content += f"Total Coffee Weight: {total_coffee_weight} kgs\n"
        content += "========================================\n\n\n"

        try:
            # Open the printer and start a document
            printer_handle = win32print.OpenPrinter(printer_name)
            job_handle = win32print.StartDocPrinter(printer_handle, 1, ("Farmers Report", None, "RAW"))
            win32print.StartPagePrinter(printer_handle)

            # Write the content to the printer
            win32print.WritePrinter(printer_handle, content.encode('utf-8'))

            # End the page and document, then close the printer
            win32print.EndPagePrinter(printer_handle)
            win32print.EndDocPrinter(printer_handle)
            win32print.ClosePrinter(printer_handle)

            messages.success(request, 'Report printed successfully.')

        except Exception as e:
            messages.error(request, f'Error printing report: {e}')

    except Exception as e:
        messages.error(request, f'Error fetching data: {e}')

    return render(request, 'admin/all_farmers.html', context)

        
def announcements(request):
    if request.method == 'POST':
        form = AnnouncementsForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data['message']
            phone_numbers = Farmer.objects.values_list('phone', flat=True)
            for phone_number in phone_numbers:
                # Send the message to each phone number
                # You'll need to implement the logic to send SMS messages here
                try:
                    send_sms(message, [phone_number])
                except Exception as e:
                    logger.error(f"Error sending SMS: {e}")
                    messages.error(request, f'Error sending SMS: {e}')
            return redirect('announcements')
    else:
        form = AnnouncementsForm()

    return render(request, 'admin/announcements.html', {'form': form})