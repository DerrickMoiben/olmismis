
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from .forms import AnnouncementsForm, HarvestForm, SeasonForm, SignupForm, LoginForm,  FarmerForm, CoffeeBerriesForm, CashierEditForm
from .models import Farmer, Field, CherryWeight, Harvest, MbuniWeight, NewPayment, Payment, Season
import logging
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.db.models import Sum
from datetime import date, datetime, time
from escpos.printer import Usb
import json
from django.conf import settings
from apis.sms import send_sms
from django.utils.timezone import now
from django.db.models import Q
from datetime import datetime
import win32print
import win32api
from board.models import  EditRequest

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
                return redirect('select_harvest')
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

# """"now unaona hii inatuma sms as per the harvest wacha ni weke njo after kutest to delete hii"""
# # Replace the win32print code in cashier_dashboard view
# @csrf_protect
# def cashier_dashboard(request):
#     # Retrieve the selected harvest from the session
#     selected_harvest_id = request.session.get('selected_harvest_id')
#     try:
#         selected_harvest = Harvest.objects.get(pk=selected_harvest_id)
#     except Harvest.DoesNotExist:
#         selected_harvest = None

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
#                         field_name="Default Field Name",
#                         harvest=selected_harvest  # Associate with the selected harvest
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

#                     # Calculate total weights
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

#                     # Prepare SMS message
#                     current_datetime = datetime.now()
#                     formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M')
#                     sms_message = (
#                         f"Dear {farmer.name}, on {formatted_datetime} you weighed {weight} kgs of {berry_type} coffee. "
#                     )
#                     if berry_type == 'cherry':
#                         sms_message += f"Your total cherry coffee weight is {berry_weight_sum} kgs."
#                     elif berry_type == 'mbuni':
#                         sms_message += f"Your total mbuni coffee weight is {berry_weight_sum} kgs."
                    
#                     try:
#                         send_sms(sms_message, [phone_number])
#                     except Exception as e:
#                         logger.error(f"Error sending SMS: {e}")
#                         messages.error(request, f'Error sending SMS: {e}')

#                     # Print receipt
#                     content = (
#                         "========================================\n"
#                         "OLMISMIS FCS Ltd\n"
#                         "========================================\n"
#                         f"Date: {current_datetime.date()}\n"
#                         f"Time: {current_datetime.strftime('%H:%M')}\n"
#                         "========================================\n"
#                         f"Farmer Name: {farmer.name}\n"
#                         f"Farmer number: {farmer.number}\n"
#                         f"Weight of the Day: {weight} kgs\n"
#                         f"Total {berry_type.capitalize()} Coffee Weight: {berry_weight_sum} kgs\n"
#                         f"Served by: {request.user.username}\n"
#                         "========================================\n\n\n"
#                     )

#                     # Use escpos to print the receipt
#                     printer = Usb(0x04b8, 0x0e15)  # Replace with your printer's Vendor ID and Product ID
#                     printer.text(content)
#                     printer.cut()

#                     messages.success(request, 'Coffee berries weight updated successfully.')
#                     return redirect('cashier-dashboard')
#                 except Exception as e:
#                     logger.error(f"Error updating coffee berries: {e}")
#                     messages.error(request, f'Error updating coffee berries: {e}')
#             else:
#                 messages.error(request, 'Farmer not found. Please enter a valid farmer number.')
#     else:
#         form = CoffeeBerriesForm()

#     return render(request, 'admin/admin_dashboard.html', {
#         'form': form,
#         'selected_harvest': selected_harvest  # Pass the selected harvest to the template
#     })

# Replace the win32print code in print_farmers_report view





# """hii sijui ni gani wacha tutest hii hapa juuh
# """
# @csrf_protect
# def cashier_dashboard(request):
#     # Retrieve the selected harvest from the session
#     selected_harvest_id = request.session.get('selected_harvest_id')
    
#     try:
#         selected_harvest = Harvest.objects.get(pk=selected_harvest_id)
#     except Harvest.DoesNotExist:
#         selected_harvest = None
    
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
#                         field_name="Default Field Name",
#                         harvest=selected_harvest  # Associate with the selected harvest
#                     )
                    
#                     if berry_type == 'cherry':
#                         cherry_weight, created = CherryWeight.objects.get_or_create(
#                             field=field,
#                             defaults={'weight': weight}
#                         )
                        
#                         if not created:
#                             cherry_weight.weight += weight
#                             cherry_weight.save()
                        
#                         # Calculate total cherry weight for the entire season
#                         total_cherry_weight = round(CherryWeight.objects.filter(
#                             field__in=Field.objects.filter(farmer=farmer)
#                         ).aggregate(Sum('weight'))['weight__sum'] or 0, 1)
                    
#                     elif berry_type == 'mbuni':
#                         mbuni_weight, created = MbuniWeight.objects.get_or_create(
#                             field=field,
#                             defaults={'weight': weight}
#                         )
                        
#                         if not created:
#                             mbuni_weight.weight += weight
#                             mbuni_weight.save()
                        
#                         # Calculate total mbuni weight for the entire season
#                         total_mbuni_weight = round(MbuniWeight.objects.filter(
#                             field__in=Field.objects.filter(farmer=farmer)
#                         ).aggregate(Sum('weight'))['weight__sum'] or 0, 1)

                    
#                     # Calculate total weights for the selected harvest
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
                    
#                     # Prepare SMS message
#                     current_datetime = datetime.now()
#                     formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M')
#                     sms_message = (
#                         f"Dear {farmer.name}, on {formatted_datetime} you weighed {weight} kgs of {berry_type} coffee. "
#                     )
                    
#                     if berry_type == 'cherry':
#                         sms_message += f"Your total  coffee cherry weight for the season is {total_cherry_weight} kgs."
#                     elif berry_type == 'mbuni':
#                         sms_message += f"Your total  coffee  mbuni weight for the season is {total_mbuni_weight} kgs."
                    
#                     try:
#                         send_sms(sms_message, [phone_number])
#                         messages.success(request, f'mesage sent succefully')
#                     except Exception as e:
#                         logger.error(f"Error sending SMS: {e}")
#                         # messages.error(request, f'Error sending SMS: {e}')
                    
#                     if berry_type == 'cherry':
#                         content = (
#                             "========================================\n"
#                             "OLMISMIS FCS Ltd\n"
#                             "========================================\n"
#                             f"Date: {current_datetime.strftime('%Y-%m-%d')}\n"
#                             f"Time: {current_datetime.strftime('%H:%M')}\n"
#                             "========================================\n"
#                             f"Farmer Name: {farmer.name}\n"
#                             f"Farmer number: {farmer.number}\n"
#                             f"Weight of the Day: {weight} kgs\n"
#                             f"Total  Coffee Cherry Weight: {total_cherry_weight} kgs\n"
#                             f"Type of Coffee: {berry_type}\n"
#                             f"Served by: {request.user.username}\n"
#                             "========================================\n\n\n"
#                         )
                    
#                     elif berry_type == 'mbuni':
#                         content = (
#                             "========================================\n"
#                             "OLMISMIS FCS Ltd\n"
#                             "========================================\n"
#                             f"Date: {current_datetime.strftime('%Y-%m-%d')}\n"
#                             f"Time: {current_datetime.strftime('%H:%M')}\n"
#                             "========================================\n"
#                             f"Farmer Name: {farmer.name}\n"
#                             f"Farmer number: {farmer.number}\n"
#                             f"Weight of the Day: {weight} kgs\n"
#                             f"Total Mbuni Coffee Weight: {total_mbuni_weight} kgs\n"
#                             f"Type of Coffee: {berry_type}\n"
#                             f"Served by: {request.user.username}\n"
#                             "========================================\n\n\n"
#                         )
                    
#                     cut_paper = "\x1d\x56\x41\x10"
#                     full_content = content + cut_paper
                    
#                     printer_name = "POS Printer 80250 Series"
#                     printer_handle = win32print.OpenPrinter(printer_name)
#                     job_handle = win32print.StartDocPrinter(printer_handle, 1, ("Receipt", None, "RAW"))
#                     win32print.StartPagePrinter(printer_handle)
#                     win32print.WritePrinter(printer_handle, full_content.encode('utf-8'))
#                     win32print.EndPagePrinter(printer_handle)
#                     win32print.EndDocPrinter(printer_handle)
#                     win32print.ClosePrinter(printer_handle)
#                 except Exception as e:
#                     logger.error(f"Error printing receipt: {e}")
#                     messages.error(request, f'Error printing receipt: {e}')
            
#             messages.success(request, 'Coffee berries weight updated successfully.')
#             return redirect('cashier-dashboard')
        
#         else:
#             messages.error(request, 'Farmer not found. Please enter a valid farmer number.')
    
#     else:
#         form = CoffeeBerriesForm()
    
#     return render(request, 'admin/admin_dashboard.html', {
#         'form': form,
#         'selected_harvest': selected_harvest  # Pass the selected harvest to the template
#     })


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
            content += f"Total Cherry Weight: {farmer.total_cherry_weight} kgs\n"
            content += f"Total Mbuni Weight: {farmer.total_mbuni_weight} kgs\n"
            content += "========================================\n"
        content += f"Total Cherry Weight: {total_cherry_weight} kgs\n"
        content += f"Total Mbuni Weight: {total_mbuni_weight} kgs\n"
        content += "========================================\n\n\n"

        try:
            # Use escpos to print the report
            printer = Usb(0x04b8, 0x0e15)  # Replace with your printer's Vendor ID and Product ID
            printer.text(content)
            printer.cut()

            messages.success(request, 'Report printed successfully.')

        except Exception as e:
            messages.error(request, f'Error printing report: {e}')

    except Exception as e:
        messages.error(request, f'Error fetching data: {e}')

    return render(request, 'admin/cashier_farmers.html', context)


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
    # Retrieve the selected harvest from the session
    selected_harvest_id = request.session.get('selected_harvest_id')
    try:
        selected_harvest = Harvest.objects.get(pk=selected_harvest_id)
    except Harvest.DoesNotExist:
        selected_harvest = None

    # Retrieve and sort all farmers by their number
    farmers = Farmer.objects.all().order_by('number')  # Order by farmer number

    # Search functionality
    search_farmer = request.GET.get('search', '')
    if search_farmer:
        farmers = farmers.filter(name__icontains=search_farmer).order_by('number')  # Filter and order by number

    # Prepare a list to hold farmer data with weights
    farmer_data = []
    total_cherry_weight = 0
    total_mbuni_weight = 0

    # Calculate weights for each farmer based on the selected harvest
    for farmer in farmers:
        # Initialize weights to zero
        cherry_weight_sum = 0
        mbuni_weight_sum = 0
        
        if selected_harvest:
            farmer_fields = Field.objects.filter(farmer=farmer, harvest=selected_harvest)
            cherry_weight_sum = CherryWeight.objects.filter(field__in=farmer_fields).aggregate(Sum('weight'))['weight__sum'] or 0
            mbuni_weight_sum = MbuniWeight.objects.filter(field__in=farmer_fields).aggregate(Sum('weight'))['weight__sum'] or 0
        
        # Append farmer data to the list
        farmer_data.append({
            'farmer': farmer,
            'cherry_weight_sum': cherry_weight_sum,
            'mbuni_weight_sum': mbuni_weight_sum,
        })

        # Update total weights
        total_cherry_weight += cherry_weight_sum
        total_mbuni_weight += mbuni_weight_sum

    return render(request, 'admin/cashier_farmers.html', {
        'farmer_data': farmer_data,
        'selected_harvest': selected_harvest,  # Pass the selected harvest to the template
        'total_cherry_weight': total_cherry_weight,
        'total_mbuni_weight': total_mbuni_weight,
    })


@csrf_protect
def create_harvest(request):
    if request.method == 'POST':
        form = HarvestForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Harvest created successfully.')
            return redirect('manage_harvests')
    else:
        form = HarvestForm()
    return render(request, 'admin/create_harvest.html', {'form': form})

@csrf_protect
def update_harvest(request, harvest_id):
    harvest = get_object_or_404(Harvest, id=harvest_id)
    if request.method == 'POST':
        form = HarvestForm(request.POST, instance=harvest)
        if form.is_valid():
            form.save()
            messages.success(request, 'Harvest updated successfully.')
            return redirect('manage_harvests')
    else:
        form = HarvestForm(instance=harvest)
    return render(request, 'admin/update_harvest.html', {'form': form, 'harvest': harvest})



@csrf_protect
def create_season(request):
    if request.method == 'POST':
        form = SeasonForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Season created successfully.')
            return redirect('manage_harvests')
    else:
        form = SeasonForm()
    return render(request, 'admin/create_season.html', {'form': form})

@csrf_protect
def update_season(request, season_id):
    season = get_object_or_404(Season, id=season_id)
    if request.method == 'POST':
        form = SeasonForm(request.POST, instance=season)
        if form.is_valid():
            form.save()
            messages.success(request, 'Season updated successfully.')
            return redirect('manage_harvests')
    else:
        form = SeasonForm(instance=season)
    return render(request, 'admin/update_season.html', {'form': form, 'season': season})


# Optionally, uncomment this if using UserSelectedHarvest model
# from .models import UserSelectedHarvest

def select_harvest(request):
    if request.method == 'POST':
        selected_harvest_id = request.POST.get('harvest')
        try:
            selected_harvest = Harvest.objects.get(pk=selected_harvest_id)

            # Option 1: Store selection in session (if not using UserSelectedHarvest model)
            request.session['selected_harvest_id'] = selected_harvest_id

            # Option 2: Save selection to UserSelectedHarvest model (if using the model)
            # user_selected_harvest, created = UserSelectedHarvest.objects.get_or_create(
            #     user=request.user, harvest=selected_harvest
            # )

            messages.success(request, f"Harvest '{selected_harvest.name}' selected successfully.")
            return redirect('cashier-dashboard')  # Redirect to your harvest management view
        except Harvest.DoesNotExist:
            messages.error(request, 'Invalid harvest selection. Please try again.')
    else:
        today = date.today()  # Get current date

        # Filter harvests based on active seasons
        active_seasons = Season.objects.filter(
            Q(start_date__lte=today) & (Q(end_date__gte=today) | Q(end_date__isnull=True))
        )  # Include seasons with open-ended dates
        harvests = Harvest.objects.filter(season__in=active_seasons)

        # Option 1: Retrieve harvest from session (if using session storage)
        selected_harvest_id = request.session.get('selected_harvest_id')

        # Option 2: Retrieve harvest from UserSelectedHarvest model (if using the model)
        # try:
        #     user_selected_harvest = UserSelectedHarvest.objects.get(user=request.user)
        #     selected_harvest = user_selected_harvest.harvest
        # except UserSelectedHarvest.DoesNotExist:
        #     selected_harvest = None

        return render(request, 'admin/select_harvest.html', {'harvests': harvests, 'selected_harvest_id': selected_harvest_id})


def manage_harvests(request):
    seasons = Season.objects.all().order_by('-start_date')  # Order by start date (descending)
    harvests = Harvest.objects.select_related('season')  # Optimize query with select_related
    return render(request, 'admin/manage_harvests.html', {'seasons': seasons, 'harvests': harvests})


def delete_season(request, pk):
    try:
        season = Season.objects.get(pk=pk)
        season.delete()
        messages.success(request, 'Season deleted successfully.')
    except Season.DoesNotExist:
        messages.error(request, 'Season not found.')
    return redirect('manage_harvests')

def delete_harvest(request, pk):
    try:
        harvest = Harvest.objects.get(pk=pk)
        harvest.delete()
        messages.success(request, 'Harvest deleted successfully.')
    except Harvest.DoesNotExist:
        messages.error(request, 'Harvest not found.')
    return redirect('manage_harvests')




def select_harvest_for_payment(request):
    today = date.today()  # Get current date

    # Filter harvests based on active seasons
    active_seasons = Season.objects.filter(
        Q(start_date__lte=today) & (Q(end_date__gte=today) | Q(end_date__isnull=True))
    )  # Include seasons with open-ended dates
    harvests = Harvest.objects.filter(season__in=active_seasons)

    if request.method == 'POST':
        selected_harvest_id = request.POST.get('harvest')
        try:
            selected_harvest = Harvest.objects.get(pk=selected_harvest_id)

            # Store selection in session
            request.session['selected_harvest_id'] = selected_harvest_id

            messages.success(request, f"Harvest '{selected_harvest.name}' selected successfully.")
            return redirect('process_payments', selected_harvest_id=selected_harvest.id)  # Redirect to payment processing view
        except Harvest.DoesNotExist:
            messages.error(request, 'Invalid harvest selection. Please try again.')

    # Optionally retrieve the selected harvest from the session
    selected_harvest_id = request.session.get('selected_harvest_id')

    return render(request, 'admin/select_harvest.html', {'harvests': harvests, 'selected_harvest_id': selected_harvest_id})

# from django.shortcuts import render
# from django.contrib import messages
# from .models import Payment, Farmer, Harvest, CherryWeight, MbuniWeight, Field

# def process_payments(request, selected_harvest_id):
#     selected_harvest = Harvest.objects.get(id=selected_harvest_id)

#     if request.method == 'POST':
#         berry_type = request.POST.get('berry_type')
#         price_per_kilo = float(request.POST.get('price_per_kilo'))
#         payment_name = request.POST.get('payment_name')

#         payment_summary = []
#         farmers = Farmer.objects.all()

#         total_kapkures_deduction = 0
#         total_blue_hills_deduction = 0
#         total_net_payment = 0

#         for farmer in farmers:
#             fields = Field.objects.filter(farmer=farmer, harvest=selected_harvest)

#             total_payment = 0

#             for field in fields:
#                 if berry_type == 'cherry':
#                     cherry_weight = CherryWeight.objects.filter(field=field).first()
#                     if cherry_weight:
#                         total_payment += price_per_kilo * cherry_weight.weight
#                 elif berry_type == 'mbuni':
#                     mbuni_weight = MbuniWeight.objects.filter(field=field).first()
#                     if mbuni_weight:
#                         total_payment += price_per_kilo * mbuni_weight.weight

#             agreement = farmer.agreement

#             kapkures_deduction = 0
#             blue_hills_deduction = 0

#             if agreement == 'Kapkures AGC':
#                 kapkures_deduction = total_payment * 0.10
#             elif agreement == 'Blue Hills AGC':
#                 blue_hills_deduction = total_payment * 0.10

#             amount_received = total_payment - (kapkures_deduction + blue_hills_deduction)

#             payment = Payment.objects.create(
#                 farmer=farmer,
#                 harvest=selected_harvest,
#                 church=agreement,
#                 berry_type=berry_type,
#                 amount=total_payment,
#                 amount_received=amount_received,
#                 price_per_kilo=price_per_kilo,
#                 payment_number=payment_name  # Set the payment name here
#             )

#             payment_summary.append({
#                 'id': payment.id,
#                 'farmer_number': farmer.number,
#                 'farmer_name': farmer.name,
#                 'kapkures_deduction': kapkures_deduction,
#                 'blue_hills_deduction': blue_hills_deduction,
#                 'net_payment': amount_received
#             })

#             total_kapkures_deduction += kapkures_deduction
#             total_blue_hills_deduction += blue_hills_deduction
#             total_net_payment += amount_received

#         # Pass the most recent payment or one for the day
#         recent_payment = payment_summary[-1] if payment_summary else None

#         messages.success(request, 'Payments processed successfully.')
#         return render(request, 'admin/payment_summary.html', {
#             'payment_summary': payment_summary,
#             'selected_harvest': selected_harvest,
#             'total_kapkures_deduction': total_kapkures_deduction,
#             'total_blue_hills_deduction': total_blue_hills_deduction,
#             'total_net_payment': total_net_payment,
#             'recent_payment': recent_payment
#         })

#     return render(request, 'admin/payment_form.html', {'selected_harvest': selected_harvest})



def cashier_edit_weight(request):
    # Retrieve the selected harvest from the session
    selected_harvest_id = request.session.get('selected_harvest_id')
    selected_harvest = Harvest.objects.filter(pk=selected_harvest_id).first() if selected_harvest_id else None

    if request.method == 'POST':
        edit_form = CashierEditForm(request.POST, selected_harvest_id=selected_harvest_id)  # Pass the harvest ID
        if edit_form.is_valid():
            # Create an EditRequest instead of directly updating the weight
            edit_request = EditRequest(
                farmer=edit_form.cleaned_data['farmer'],
                berry_type=edit_form.cleaned_data['berry_type'],
                current_weight=edit_form.cleaned_data['current_weight'],
                new_weight=edit_form.cleaned_data['new_weight'],
                harvest=selected_harvest,
                cashier=request.user  # Assuming the cashier is logged in
            )
            edit_request.save()

            messages.success(request, 'Edit request submitted successfully.')
            return redirect('cashier-dashboard')

    else:
        edit_form = CashierEditForm(selected_harvest_id=selected_harvest_id)  # Pass the harvest ID

    return render(request, 'edit_weight.html', {
        'edit_form': edit_form,
        'selected_harvest': selected_harvest
    })



# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Payment

def list_payments(request):
    payments = Payment.objects.all()
    return render(request, 'admin/list_payments.html', {'payments': payments})

def delete_payment(request, payment_id):
    try:
        payment = get_object_or_404(Payment, id=payment_id)
        payment.delete()
        messages.success(request, 'Payment deleted successfully.')
    except Exception as e:
        messages.error(request, f'Failed to delete payment: {str(e)}')
    return redirect('list_payments')

def delete_all_payments(request):
    try:
        remove = Payment.objects.all()
        remove.delete()
        messages.success(request, "All payment have been deleted so far")
    except Exception as e:
        messages.error(request, f'Failed to  delete all of the payments: {str(e)}')

    return redirect('list_payments')


from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse
import win32print
import win32ui
from .models import Payment

def print_payment_report(request, payment_number):
    # Fetch the payment using the payment_number
    payment = get_object_or_404(Payment, payment_number=payment_number)

    # Define the printer name
    printer_name = "EPSON L3250 Series"
    
    # Create a print job
    try:
        # Open the printer
        printer = win32print.OpenPrinter(printer_name)
        try:
            # Start the print job
            hPrinter = win32print.StartDocPrinter(printer, 1, ("Payment Report", None, "RAW"))
            try:
                win32print.StartPagePrinter(printer)

                # Create the report
                report = f"Payment Report for {payment.payment_number}\n"
                report += f"Farmer: {payment.farmer.name}\n"
                report += f"Harvest: {payment.harvest.name}\n"
                report += f"Berries: {payment.berry_type}\n"
                report += f"Amount: {payment.amount}\n"
                report += f"Amount Received: {payment.amount_received}\n"
                report += f"Price per Kilo: {payment.price_per_kilo}\n"
                report += f"Church: {payment.church}\n"

                # Print the report
                win32print.WritePrinter(printer, report.encode())
                win32print.EndPagePrinter(printer)
                win32print.EndDocPrinter(printer)
            finally:
                win32print.ClosePrinter(printer)
        except Exception as e:
            return HttpResponse(f"Failed to start document: {e}")
    except Exception as e:
        return HttpResponse(f"Failed to open printer: {e}")

    return redirect('select_harvest_for_payment')  # Redirect to the payment summary page

from django.contrib import messages
from django.shortcuts import render
from .models import Harvest, Farmer, Field, CherryWeight, MbuniWeight, Payment

# def process_payments(request, selected_harvest_id):
#     selected_harvest = Harvest.objects.get(id=selected_harvest_id)

#     if request.method == 'POST':
#         berry_type = request.POST.get('berry_type')
#         price_per_kilo = float(request.POST.get('price_per_kilo'))
#         payment_number = request.POST.get('payment_number')

#         print(f"Payment Number: {payment_number}")  # 

#         payment_summary = []
#         farmers = Farmer.objects.all()

#         total_kapkures_deduction = 0
#         total_blue_hills_deduction = 0
#         total_net_payment = 0

#         for farmer in farmers:
#             fields = Field.objects.filter(farmer=farmer, harvest=selected_harvest)

#             total_payment = 0

#             for field in fields:
#                 if berry_type == 'cherry':
#                     cherry_weight = CherryWeight.objects.filter(field=field).first()
#                     if cherry_weight:
#                         total_payment += price_per_kilo * cherry_weight.weight
#                 elif berry_type == 'mbuni':
#                     mbuni_weight = MbuniWeight.objects.filter(field=field).first()
#                     if mbuni_weight:
#                         total_payment += price_per_kilo * mbuni_weight.weight

#             agreement = farmer.agreement

#             kapkures_deduction = 0
#             blue_hills_deduction = 0

#             if agreement == 'Kapkures AGC':
#                 kapkures_deduction = total_payment * 0.10
#             elif agreement == 'Blue Hills AGC':
#                 blue_hills_deduction = total_payment * 0.10

#             amount_received = total_payment - (kapkures_deduction + blue_hills_deduction)

#             payment = Payment.objects.create(
#                 farmer=farmer,
#                 harvest=selected_harvest,
#                 church=agreement,
#                 berry_type=berry_type,
#                 amount=total_payment,
#                 amount_received=amount_received,
#                 price_per_kilo=price_per_kilo,
#                 payment_number=payment_number  # Set the payment name here
#             )

            

#             payment_summary.append({
#                 'id': payment.id,
#                 'farmer_number': farmer.number,
#                 'farmer_name': farmer.name,
#                 'kapkures_deduction': kapkures_deduction,
#                 'blue_hills_deduction': blue_hills_deduction,
#                 'net_payment': amount_received,
#                 'payment_number': payment_number
#             })

#             total_kapkures_deduction += kapkures_deduction
#             total_blue_hills_deduction += blue_hills_deduction
#             total_net_payment += amount_received

#             # After processing payments, add this line  # Check the content of recent_payment


#         # Pass the most recent payment or one for the day
#         recent_payment = payment_summary[-1] if payment_summary else None

#         # After processing payments, add this line
#         print(f"Recent Payment: {recent_payment}")  # Check the content of recent_payment


#         messages.success(request, 'Payments processed successfully.')
#         return render(request, 'admin/payment_summary.html', {
#             'payment_summary': payment_summary,
#             'selected_harvest': selected_harvest,
#             'total_kapkures_deduction': total_kapkures_deduction,
#             'total_blue_hills_deduction': total_blue_hills_deduction,
#             'total_net_payment': total_net_payment,
#             'recent_payment': recent_payment
#         })

#     return render(request, 'admin/payment_form.html', {'selected_harvest': selected_harvest})



from django.shortcuts import render
from django.contrib import messages
from .models import Farmer, Harvest, NewPayment, CherryWeight, MbuniWeight, Field

def process_payments(request, selected_harvest_id):
    selected_harvest = Harvest.objects.get(id=selected_harvest_id)
    
    if request.method == 'POST':
        berry_type = request.POST.get('berry_type')
        price_per_kilo = float(request.POST.get('price_per_kilo'))
        payment_number = request.POST.get('payment_number')

        payment_summary = []
        farmers = Farmer.objects.all()
        total_kapkures_deduction = 0
        total_blue_hills_deduction = 0
        total_net_payment = 0

        for farmer in farmers:
            fields = Field.objects.filter(farmer=farmer, harvest=selected_harvest)
            total_payment = 0

            for field in fields:
                if berry_type == 'cherry':
                    cherry_weight = CherryWeight.objects.filter(field=field).first()
                    if cherry_weight:
                        total_payment += price_per_kilo * cherry_weight.weight
                elif berry_type == 'mbuni':
                    mbuni_weight = MbuniWeight.objects.filter(field=field).first()
                    if mbuni_weight:
                        total_payment += price_per_kilo * mbuni_weight.weight

            agreement = farmer.agreement
            kapkures_deduction = round(total_payment * 0.10, 1) if agreement == 'Kapkures AGC' else 0
            blue_hills_deduction = round(total_payment * 0.10, 1) if agreement == 'Blue Hills AGC' else 0
            amount_received = round(total_payment - (kapkures_deduction + blue_hills_deduction), 1)

            # Create a new payment record
            NewPayment.objects.create(
                farmer=farmer,
                harvest=selected_harvest,
                church=agreement,
                berry_type=berry_type,
                amount=total_payment,
                amount_received=amount_received,
                price_per_kilo=price_per_kilo,
                payment_number=payment_number
            )

            payment_summary.append({
                'farmer_number': farmer.number,
                'farmer_name': farmer.name,
                'kapkures_deduction': kapkures_deduction,
                'blue_hills_deduction': blue_hills_deduction,
                'net_payment': amount_received,
                'payment_number': payment_number
            })

            total_kapkures_deduction += kapkures_deduction
            total_blue_hills_deduction += blue_hills_deduction
            total_net_payment += amount_received

        # Sort payment summary by farmer number
        payment_summary.sort(key=lambda x: x['farmer_number'])

        # Store payment summary in session
        request.session['payment_summary'] = payment_summary
        request.session['total_kapkures_deduction'] = round(total_kapkures_deduction, 1)
        request.session['total_blue_hills_deduction'] = round(total_blue_hills_deduction, 1)
        request.session['total_net_payment'] = round(total_net_payment, 1)

        messages.success(request, 'Payments processed successfully. You can now print the summary.')
        return render(request, 'admin/payment_summary.html', {
            'payment_summary': payment_summary,
            'selected_harvest': selected_harvest,
            'total_kapkures_deduction': round(total_kapkures_deduction, 1),
            'total_blue_hills_deduction': round(total_blue_hills_deduction, 1),
            'total_net_payment': round(total_net_payment, 1)
        })

    return render(request, 'admin/payment_form.html', {'selected_harvest': selected_harvest})

def print_payment_summary(request):
    payment_summary = request.session.get('payment_summary', [])
    total_kapkures_deduction = request.session.get('total_kapkures_deduction', 0)
    total_blue_hills_deduction = request.session.get('total_blue_hills_deduction', 0)
    total_net_payment = request.session.get('total_net_payment', 0)

    return render(request, 'admin/payment_summary_print.html', {
        'payment_summary': payment_summary,
        'total_kapkures_deduction': round(total_kapkures_deduction, 1),
        'total_blue_hills_deduction': round(total_blue_hills_deduction, 1),
        'total_net_payment': round(total_net_payment, 1),
    })




@csrf_protect
def cashier_dashboard(request):
    # Retrieve the selected harvest from the session
    selected_harvest_id = request.session.get('selected_harvest_id')
    
    try:
        selected_harvest = Harvest.objects.get(pk=selected_harvest_id)
    except Harvest.DoesNotExist:
        selected_harvest = None
    
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
                    # Ensure there's a default field for the farmer associated with the selected harvest
                    field, created = Field.objects.get_or_create(
                        farmer=farmer,
                        field_name="Default Field Name",
                        harvest=selected_harvest  # Associate with the selected harvest
                    )
                    
                    if berry_type == 'cherry':
                        cherry_weight, created = CherryWeight.objects.get_or_create(
                            field=field,
                            defaults={'weight': weight}
                        )
                        
                        if not created:
                            cherry_weight.weight += weight
                            cherry_weight.save()

                        # Calculate total cherry weight for the entire season across all active harvests
                        farmer_fields = Field.objects.filter(farmer=farmer, harvest__season=selected_harvest.season)
                        total_cherry_weight = round(CherryWeight.objects.filter(
                            field__in=farmer_fields
                        ).aggregate(Sum('weight'))['weight__sum'] or 0, 1)
                    
                    elif berry_type == 'mbuni':
                        mbuni_weight, created = MbuniWeight.objects.get_or_create(
                            field=field,
                            defaults={'weight': weight}
                        )
                        
                        if not created:
                            mbuni_weight.weight += weight
                            mbuni_weight.save()

                        # Calculate total mbuni weight for the entire season across all active harvests
                        farmer_fields = Field.objects.filter(farmer=farmer, harvest__season=selected_harvest.season)
                        total_mbuni_weight = round(MbuniWeight.objects.filter(
                            field__in=farmer_fields
                        ).aggregate(Sum('weight'))['weight__sum'] or 0, 1)

                    # Calculate total weights for the selected harvest (if needed)
                    cherry_weight_sum = CherryWeight.objects.filter(
                        field__in=Field.objects.filter(farmer=farmer, harvest=selected_harvest)
                    ).aggregate(Sum('weight'))['weight__sum'] or 0
                    
                    mbuni_weight_sum = MbuniWeight.objects.filter(
                        field__in=Field.objects.filter(farmer=farmer, harvest=selected_harvest)
                    ).aggregate(Sum('weight'))['weight__sum'] or 0
                    
                    total_coffee_weight = cherry_weight_sum + mbuni_weight_sum
                    farmer.total_coffee_weight = total_coffee_weight
                    farmer.save()

                    # Prepare SMS message
                    current_datetime = datetime.now()
                    formatted_datetime = current_datetime.strftime('%Y-%m-%d %H:%M')
                    sms_message = (
                        f"Dear {farmer.name}, on {formatted_datetime} you weighed {weight} kgs of {berry_type} coffee. "
                    )
                    
                    if berry_type == 'cherry':
                        sms_message += f"Your total coffee cherry weight for the season is {total_cherry_weight} kgs."
                    elif berry_type == 'mbuni':
                        sms_message += f"Your total coffee mbuni weight for the season is {total_mbuni_weight} kgs."
                    
                    try:
                        send_sms(sms_message, [phone_number])
                        messages.success(request, 'Message sent successfully.')
                    except Exception as e:
                        logger.error(f"Error sending SMS: {e}")
                        # messages.error(request, f'Error sending SMS: {e}')
                    
                    # Prepare the content for printing based on the berry type
                    content = (
                        "========================================\n"
                        "OLMISMIS FCS Ltd\n"
                        "========================================\n"
                        f"Date: {current_datetime.strftime('%Y-%m-%d')}\n"
                        f"Time: {current_datetime.strftime('%H:%M')}\n"
                        "========================================\n"
                        f"Farmer Name: {farmer.name}\n"
                        f"Farmer number: {farmer.number}\n"
                        f"Weight of the Day: {weight} kgs\n"
                    )
                    
                    if berry_type == 'cherry':
                        content += f"Total Coffee Cherry Weight: {total_cherry_weight} kgs\n"
                    elif berry_type == 'mbuni':
                        content += f"Total Mbuni Coffee Weight: {total_mbuni_weight} kgs\n"
                    
                    content += (
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
        
        else:
            messages.error(request, 'Farmer not found. Please enter a valid farmer number.')
    
    else:
        form = CoffeeBerriesForm()
    
    return render(request, 'admin/admin_dashboard.html', {
        'form': form,
        'selected_harvest': selected_harvest  # Pass the selected harvest to the template
    })
