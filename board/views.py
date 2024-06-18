from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from  dashboard.models import Farmer, Field, CoffeeBerries
import logging
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.db.models import Sum
from datetime import datetime
from apis.sms import send_sms
from escpos.printer import Usb
import json


# Create your views here.
def admin(request):
    return render(request, 'admin.html')

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

        # Initialize the printer
        printer = Usb(0x0fe6, 0x811e, in_ep=0x82, out_ep=0x01)

        try:
            # Set text style and alignment
            printer.set(align='center', font='b', width=4, height=6)

            # Print header
            printer.text("========================================\n")
            printer.text("OLMISMIS FCS Ltd\n")
            printer.text("========================================\n")
            printer.text("Farmers Report\n")
            printer.text("========================================\n")

            # Print each farmer's details
            for farmer in farmers:
                printer.text(f"Farmer Name: {farmer.name}\n")
                printer.text(f"Farmer Number: {farmer.number}\n")
                printer.text(f"Total Coffee Weight: {farmer.coffee_weight} kgs\n")
                printer.text("========================================\n")

            # Print total coffee weight
            printer.text(f"Total Coffee Weight: {total_coffee_weight} kgs\n")
            printer.text("========================================\n\n\n")
            printer.cut()

            messages.success(request, 'Report printed successfully.')

        except Exception as e:
            messages.error(request, f'Error printing report: {e}')

        finally:
            # Close the printer
            try:
                printer.close()
            except Exception as e:
                messages.error(request, f'Error closing printer: {e}')

    except Exception as e:
        messages.error(request, f'Error fetching data: {e}')

    return render(request, 'all_farmers.html', context)