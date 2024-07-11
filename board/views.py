import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from dashboard.models import Farmer, Field, CoffeeBerries
from dashboard.forms import FarmerForm
from .forms import SignupForm, LoginboardForm
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.db.models import Sum, F
from django.contrib.auth.decorators import login_required
from apis.sms import send_sms
from escpos.printer import Usb
from datetime import datetime, timedelta
import win32print

logger = logging.getLogger(__name__)

@csrf_protect
def singup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = True  # Ensure the user is marked as staff
            user.save()
            messages.success(request, 'The board member has been signed up successfully.')
            return redirect('admin_login')
        else:
            logger.error('Error during sign up.')
            messages.error(request, 'There was an error trying to sign up the board member.')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})

@csrf_protect
@csrf_protect
def admin_login(request):
    if request.method == 'POST':
        form = LoginboardForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # Additional debugging logs
            logger.info(f"Attempting login for username: {username}")

            board = authenticate(username=username, password=password)
            if board is not None and board.is_staff:
                login(request, board)
                logger.info(f"User {username} logged in successfully.")
                return redirect('admin_dashboard')
            else:
                logger.error('Unsuccessful login attempt.')
                messages.error(request, 'Invalid username or password.')
        else:
            logger.error('Form is not valid.')
            messages.error(request, 'Invalid form submission.')
    else:
        form = LoginboardForm()
    return render(request, 'login.html', {'form': form})

@login_required
@csrf_protect
def admin_dashboard(request):
    search_query = request.GET.get('search_query', '')
    farmers = []

    if search_query:
        farmers = Farmer.objects.filter(name__icontains=search_query)

    # Total number of farmers
    total_farmers = Farmer.objects.count()

    # Total coffee weight
    total_coffee_weight = Farmer.objects.aggregate(
        total_weight=Sum(F('field__coffeeberries__weight'))
    )['total_weight'] or 0

    context = {
        'total_farmers': total_farmers,
        'total_coffee_weight': total_coffee_weight,
        'farmers': farmers,
        'search_query': search_query,
    }
    return render(request, 'indexboard.html', context)


@csrf_protect
def all_farmers(request):
    search_query = request.GET.get('search', '')
    if search_query:
        farmers = Farmer.objects.filter(name__icontains=search_query)
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
        'search_query': search_query,
    }
    return render(request, 'all_farmers.html', context)

@csrf_protect
def delete_farmer(request, farmer_id):
    farmer = get_object_or_404(Farmer, id=farmer_id)
    farmer.delete()
    messages.success(request, 'Farmer deleted successfully.')
    return redirect('all-farmers')

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

    return render(request, 'all_farmers.html', context)

@login_required
@csrf_protect
def edit_farmer(request, farmer_id):
    farmer = get_object_or_404(Farmer, id=farmer_id)

    if request.method == 'POST':
        form = FarmerForm(request.POST, instance=farmer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Farmer details updated successfully.')
            return redirect('admin_dashboard')
    else:
        form = FarmerForm(instance=farmer)

    context = {
        'form': form,
        'farmer': farmer,
    }
    return render(request, 'edit_farmer.html', context)