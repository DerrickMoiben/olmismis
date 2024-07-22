from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from .forms import AnnouncementsForm, SignupForm, LoginForm,  FarmerForm, CoffeeBerriesForm
from .models import Farmer, Field, CherryWeight, MbuniWeight
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
from django.utils.timezone import now

logger = logging.getLogger(__name__)


def land_page(request):
    return render(request, 'index.html')

@csrf_protect
def cashier_signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sign up successfully')
            return redirect('cashier-login')
        else:
            messages.error(request, 'Sign up was unseccefull')
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
            user = authenticate(username=username, password=password)
            logger.info(f"Username: {username}, Password: {password}, User: {user}")
            if user:
                login(request, user)
                return redirect('cashier-dashboard')
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
                response = send_sms(f"Dear {farmer.name}, you have been registered successfully at OLMISMIS FCS Ltd new Software System. Your number is {farmer.number}.", [farmer.phone])
                if response == "Insufficient balance":
                    messages.warning(request, 'Failed to send SMS: Insufficient balance.')
                else:
                    pass

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


    

# @csrf_protect
# def cashier_dashboard(request):
#     farmers = Farmer.objects.all()
    
#     if request.method == 'POST':
#         form = CoffeeBerriesForm(request.POST)
#         if form.is_valid():
#             farmer_number = form.cleaned_data['farmer_number']
#             berry_type = form.cleaned_data['berry_type']
#             weight = form.cleaned_data['weight']
            
#             farmer = Farmer.objects.filter(number=farmer_number).first()
#             if farmer:
#                 phone_number = farmer.phone
#                 try:
#                     # Ensure there's a default field for the farmer
#                     field, created = Field.objects.get_or_create(
#                         farmer=farmer, 
#                         field_name="Default Field Name"
#                     )
                    
#                     if berry_type == 'cherry':
#                         cherry_weight, created = CherryWeight.objects.get_or_create(
#                             field=field, 
#                             defaults={'weight': weight}
#                         )
#                         if not created:
#                             cherry_weight.weight += weight
#                             cherry_weight.save()
#                         berry_weight_sum = CherryWeight.objects.filter(
#                             field__in=Field.objects.filter(farmer=farmer)
#                         ).aggregate(Sum('weight'))['weight__sum'] or 0
#                     elif berry_type == 'mbuni':
#                         mbuni_weight, created = MbuniWeight.objects.get_or_create(
#                             field=field, 
#                             defaults={'weight': weight}
#                         )
#                         if not created:
#                             mbuni_weight.weight += weight
#                             mbuni_weight.save()
#                         berry_weight_sum = MbuniWeight.objects.filter(
#                             field__in=Field.objects.filter(farmer=farmer)
#                         ).aggregate(Sum('weight'))['weight__sum'] or 0

#                     farmer_fields = Field.objects.filter(farmer=farmer)
#                     cherry_weight_sum = CherryWeight.objects.filter(
#                         field__in=farmer_fields
#                     ).aggregate(Sum('weight'))['weight__sum'] or 0
#                     mbuni_weight_sum = MbuniWeight.objects.filter(
#                         field__in=farmer_fields
#                     ).aggregate(Sum('weight'))['weight__sum'] or 0
#                     total_coffee_weight = cherry_weight_sum + mbuni_weight_sum

#                     farmer.total_coffee_weight = total_coffee_weight
#                     farmer.save()

#                     try:
#                         current_datetime = datetime.now()
#                         formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M')
#                         time = current_datetime.strftime('%H:%M')
#                         date = current_datetime.date()

#                         sms_message = (
#                             f"Dear {farmer.name}, on {formatted_datetime} you weighed {weight} kgs of {berry_type} coffee. "
#                         )
#                         if berry_type == 'cherry':
#                             sms_message += f"Your total cherry coffee weight is {berry_weight_sum} kgs."
#                         elif berry_type == 'mbuni':
#                             sms_message += f"Your total mbuni coffee weight is {berry_weight_sum} kgs."
                        
#                         try:
#                             send_sms(sms_message, [phone_number])
#                         except Exception as e:
#                             logger.error(f"Error sending SMS: {e}")
#                             messages.error(request, f'Error sending SMS: {e}')

#                         content = (
#                             "========================================\n"
#                             "OLMISMIS FCS Ltd\n"
#                             "========================================\n"
#                             f"Date: {date}\n"
#                             f"Time: {time}\n"
#                             "========================================\n"
#                             f"Farmer Name: {farmer.name}\n"
#                             f"Farmer number: {farmer.number}\n"
#                             f"Weight of the Day: {weight} kgs\n"
#                             f"Total Coffee Weight: {total_coffee_weight} kgs\n"
#                             f"Type of Coffee: {berry_type}\n"
#                             f"Served by: {request.user.username}\n"
#                             "========================================\n\n\n"
#                         )

#                         cut_paper = "\x1d\x56\x41\x10"
#                         full_content = content + cut_paper

#                         printer_name = "POS Printer 80250 Series"
#                         printer_handle = win32print.OpenPrinter(printer_name)
#                         job_handle = win32print.StartDocPrinter(printer_handle, 1, ("Receipt", None, "RAW"))
#                         win32print.StartPagePrinter(printer_handle)
#                         win32print.WritePrinter(printer_handle, full_content.encode('utf-8'))
#                         win32print.EndPagePrinter(printer_handle)
#                         win32print.EndDocPrinter(printer_handle)
#                         win32print.ClosePrinter(printer_handle)

#                     except Exception as e:
#                         logger.error(f"Error printing receipt: {e}")
#                         messages.error(request, f'Error printing receipt: {e}')
#                     messages.success(request, 'Coffee berries weight updated successfully.')
#                     return redirect('cashier-dashboard')
#                 except Exception as e:
#                     logger.error(f"Error updating coffee berries: {e}")
#                     messages.error(request, f'Error updating coffee berries: {e}')
#             else:
#                 messages.error(request, 'Farmer not found. Please enter a valid farmer number.')
#     else:
#         form = CoffeeBerriesForm()
#     return render(request, 'admin/admin_dashboard.html', {'farmers': farmers, 'form': form})

@csrf_protect
def cashier_dashboard(request):
    farmers = Farmer.objects.all()
    
    if request.method == 'POST':
        form = CoffeeBerriesForm(request.POST)
        if form.is_valid():
            farmer_number = form.cleaned_data['farmer_number']
            berry_type = form.cleaned_data['berry_type']
            weight = form.cleaned_data['weight']
            
            farmer = Farmer.objects.filter(number=farmer_number).first()
            if farmer:
                phone_number = farmer.phone
                try:
                    # Ensure there's a default field for the farmer
                    field, created = Field.objects.get_or_create(
                        farmer=farmer, 
                        field_name="Default Field Name"
                    )
                    
                    if berry_type == 'cherry':
                        cherry_weight, created = CherryWeight.objects.get_or_create(
                            field=field, 
                            defaults={'weight': weight}
                        )
                        if not created:
                            cherry_weight.weight += weight
                            cherry_weight.save()
                        berry_weight_sum = CherryWeight.objects.filter(
                            field__in=Field.objects.filter(farmer=farmer)
                        ).aggregate(Sum('weight'))['weight__sum'] or 0
                    elif berry_type == 'mbuni':
                        mbuni_weight, created = MbuniWeight.objects.get_or_create(
                            field=field, 
                            defaults={'weight': weight}
                        )
                        if not created:
                            mbuni_weight.weight += weight
                            mbuni_weight.save()
                        berry_weight_sum = MbuniWeight.objects.filter(
                            field__in=Field.objects.filter(farmer=farmer)
                        ).aggregate(Sum('weight'))['weight__sum'] or 0

                    farmer_fields = Field.objects.filter(farmer=farmer)
                    cherry_weight_sum = CherryWeight.objects.filter(
                        field__in=farmer_fields
                    ).aggregate(Sum('weight'))['weight__sum'] or 0
                    mbuni_weight_sum = MbuniWeight.objects.filter(
                        field__in=farmer_fields
                    ).aggregate(Sum('weight'))['weight__sum'] or 0
                    total_coffee_weight = cherry_weight_sum + mbuni_weight_sum

                    farmer.total_coffee_weight = total_coffee_weight
                    farmer.save()

                    try:
                        current_datetime = datetime.now()
                        formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M')
                        time = current_datetime.strftime('%H:%M')
                        date = current_datetime.date()

                        sms_message = (
                            f"Dear {farmer.name}, on {formatted_datetime} you weighed {weight} kgs of {berry_type} coffee. "
                        )
                        if berry_type == 'cherry':
                            sms_message += f"Your total cherry coffee weight is {berry_weight_sum} kgs."
                        elif berry_type == 'mbuni':
                            sms_message += f"Your total mbuni coffee weight is {berry_weight_sum} kgs."
                        
                        try:
                            send_sms(sms_message, [phone_number])
                        except Exception as e:
                            logger.error(f"Error sending SMS: {e}")
                            messages.error(request, f'Error sending SMS: {e}')

                        if berry_type == 'cherry':
                            content = (
                                "========================================\n"
                                "OLMISMIS FCS Ltd\n"
                                "========================================\n"
                                f"Date: {date}\n"
                                f"Time: {time}\n"
                                "========================================\n"
                                f"Farmer Name: {farmer.name}\n"
                                f"Farmer number: {farmer.number}\n"
                                f"Weight of the Day: {weight} kgs\n"
                                f"Total Cherry Coffee Weight: {berry_weight_sum} kgs\n"
                                f"Type of Coffee: {berry_type}\n"
                                f"Served by: {request.user.username}\n"
                                "========================================\n\n\n"
                            )
                        elif berry_type == 'mbuni':
                            content = (
                                "========================================\n"
                                "OLMISMIS FCS Ltd\n"
                                "========================================\n"
                                f"Date: {date}\n"
                                f"Time: {time}\n"
                                "========================================\n"
                                f"Farmer Name: {farmer.name}\n"
                                f"Farmer number: {farmer.number}\n"
                                f"Weight of the Day: {weight} kgs\n"
                                f"Total Mbuni Coffee Weight: {berry_weight_sum} kgs\n"
                                f"Type of Coffee: {berry_type}\n"
                                f"Served by: {request.user.username}\n"
                                "========================================\n\n\n"
                            )

                        cut_paper = "\x1d\x56\x41\x10"
                        full_content = content + cut_paper

                        printer_name = "POS Printer 80250 Series"
                        printer_handle = win32print.OpenPrinter(printer_name)
                        job_handle = win32print.StartDocPrinter(printer_handle, 1, ("Receipt", None, "RAW"))
                        win32print.StartPagePrinter(printer_handle)
                        win32print.WritePrinter(printer_handle, full_content.encode('utf-8'))
                        win32print.EndPagePrinter(printer_handle)
                        win32print.EndDocPrinter(printer_handle)
                        win32print.ClosePrinter(printer_handle)

                    except Exception as e:
                        logger.error(f"Error printing receipt: {e}")
                        messages.error(request, f'Error printing receipt: {e}')
                    messages.success(request, 'Coffee berries weight updated successfully.')
                    return redirect('cashier-dashboard')
                except Exception as e:
                    logger.error(f"Error updating coffee berries: {e}")
                    messages.error(request, f'Error updating coffee berries: {e}')
            else:
                messages.error(request, 'Farmer not found. Please enter a valid farmer number.')
    else:
        form = CoffeeBerriesForm()
    return render(request, 'admin/admin_dashboard.html', {'farmers': farmers, 'form': form})

@csrf_protect        
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


@csrf_protect
def cashier_farmers(request):
    search_farmer = request.GET.get('search', '')
    if search_farmer:
        farmers = Farmer.objects.filter(name__icontains=search_farmer)
    else:
        farmers = Farmer.objects.all()

    total_cherry_weight = 0
    total_mbuni_weight = 0

    for farmer in farmers:
        farmer_fields = farmer.field_set.all()
        farmer_cherry_weight = CherryWeight.objects.filter(field__in=farmer_fields).aggregate(Sum('weight'))['weight__sum'] or 0
        farmer_mbuni_weight = MbuniWeight.objects.filter(field__in=farmer_fields).aggregate(Sum('weight'))['weight__sum'] or 0
        farmer.total_cherry_weight = farmer_cherry_weight
        farmer.total_mbuni_weight = farmer_mbuni_weight
        total_cherry_weight += farmer_cherry_weight
        total_mbuni_weight += farmer_mbuni_weight

    context = {
        'farmers': farmers,
        'total_cherry_weight': total_cherry_weight,
        'total_mbuni_weight': total_mbuni_weight,
        'search_query': search_farmer,
    }
    return render(request, 'admin/cashier_farmers.html', context)


@csrf_protect
def print_farmers_report(request):
    try:
        farmers = Farmer.objects.all()
        total_cherry_weight = 0
        total_mbuni_weight = 0


        for farmer in farmers:
            farmer_fields = farmer.field_set.all()
            farmer_cherry_weight = CherryWeight.objects.filter(field__in=farmer_fields).aggregate(Sum('weight'))['weight__sum'] or 0
            farmer_mbuni_weight = MbuniWeight.objects.filter(field__in=farmer_fields).aggregate(Sum('weight'))['weight__sum'] or 0
            farmer.total_cherry_weight = farmer_cherry_weight
            farmer.total_mbuni_weight = farmer_mbuni_weight
            total_cherry_weight += farmer_cherry_weight
            total_mbuni_weight += farmer_mbuni_weight


        # Prepare context for rendering
        context = {
            'farmers': farmers,
            'total_cherry_weight': total_cherry_weight,
            'total_mbuni_weight': total_mbuni_weight,
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
            # content += f"Total Coffee Weight: {farmer.coffee_weight} kgs\n"
            content += f"Total Cherry Weight: { farmer.total_cherry_weight} kgs\n"
            content += f"Total Mbuni Weight: { farmer.total_mbuni_weight} kgs\n"
            content += "========================================\n"
        content += f"Total Cherry Weight: {total_cherry_weight} kgs\n"
        content += f"Total Mbuni Weight: {total_mbuni_weight} kgs\n"
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

    return render(request, 'admin/cashier_farmers.html', context)
