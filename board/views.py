import json
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from board.models import EditRequest
from dashboard.models import Farmer, CherryWeight, MbuniWeight
from dashboard.forms import FarmerForm
from .forms import FarmerAddForm, FarmerEditForm, SignupForm, LoginboardForm
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib import messages
from django.db.models import Sum, F
from django.contrib.auth.decorators import login_required
from apis.sms import send_sms
from escpos.printer import Usb
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.urls import reverse

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

@login_required
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

    # Total cherry weight
    total_cherry_weight = CherryWeight.objects.aggregate(
        total_weight=Sum('weight')
    )['total_weight'] or 0

    # Total mbuni weight
    total_mbuni_weight = MbuniWeight.objects.aggregate(
        total_weight=Sum('weight')
    )['total_weight'] or 0

    context = {
        'total_farmers': total_farmers,
        'total_cherry_weight': total_cherry_weight,
        'total_mbuni_weight': total_mbuni_weight,
        'farmers': farmers,
        'search_query': search_query,
    }
    return render(request, 'indexboard.html', context)

# @login_required
# @csrf_protect
# def all_farmers(request):
#     search_farmer = request.GET.get('search', '')
#     if search_farmer:
#         farmers = Farmer.objects.filter(name__icontains=search_farmer)
#     else:
#         farmers = Farmer.objects.all()

#     total_cherry_weight = 0
#     total_mbuni_weight = 0

#     for farmer in farmers:
#         farmer_fields = farmer.field_set.all()
#         farmer_cherry_weight = CherryWeight.objects.filter(field__in=farmer_fields).aggregate(Sum('weight'))['weight__sum'] or 0
#         farmer_mbuni_weight = MbuniWeight.objects.filter(field__in=farmer_fields).aggregate(Sum('weight'))['weight__sum'] or 0
#         farmer.total_cherry_weight = farmer_cherry_weight
#         farmer.total_mbuni_weight = farmer_mbuni_weight
#         total_cherry_weight += farmer_cherry_weight
#         total_mbuni_weight += farmer_mbuni_weight

#     context = {
#         'farmers': farmers,
#         'total_cherry_weight': total_cherry_weight,
#         'total_mbuni_weight': total_mbuni_weight,
#         'search_query': search_farmer,
#     }
#     return render(request, 'all_farmers.html', context)


@login_required
@csrf_protect
def all_farmers(request):
    search_farmer = request.GET.get('search', '')
    if search_farmer:
        farmers = Farmer.objects.filter(name__icontains=search_farmer)
    else:
        farmers = Farmer.objects.all().order_by('number')  # Sort by number

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
    return render(request, 'all_farmers.html', context)




@login_required
@csrf_protect
def delete_farmer(request, farmer_id):
    farmer = get_object_or_404(Farmer, id=farmer_id)
    farmer.delete()
    messages.success(request, 'Farmer deleted successfully.')
    return redirect('all-farmers')



@login_required
@csrf_protect
def print_farmer_report(request):
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

        # Set up the ESC/POS printer (adjust parameters according to your printer's setup)
        printer = Usb(0x04b8, 0x0202)  # Replace with your printer's vendor and product ID

        # Construct the content to be printed
        content = (
            "========================================\n"
            "OLMISMIS FCS Ltd\n"
            "========================================\n"
            "Farmers Report\n"
            "========================================\n"
        )
        for farmer in farmers:
            content += (
                f"Farmer Name: {farmer.name}\n"
                f"Farmer Number: {farmer.number}\n"
                f"Total Cherry Weight: {farmer.total_cherry_weight} kgs\n"
                f"Total Mbuni Weight: {farmer.total_mbuni_weight} kgs\n"
                "========================================\n"
            )
        content += (
            f"Total Cherry Weight: {total_cherry_weight} kgs\n"
            f"Total Mbuni Weight: {total_mbuni_weight} kgs\n"
            "========================================\n\n\n"
        )

        try:
            # Print content
            printer.text(content)
            printer.cut()
            messages.success(request, 'Report printed successfully.')

        except Exception as e:
            messages.error(request, f'Error printing report: {e}')

    except Exception as e:
        messages.error(request, f'Error fetching data: {e}')

    return render(request, 'all_farmers.html', context)


# @login_required
# @csrf_protect
# def edit_farmer(request, farmer_id):
#     farmer = get_object_or_404(Farmer, id=farmer_id)

#     if request.method == 'POST':
#         form = FarmerEditForm(request.POST, instance=farmer)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Farmer details updated successfully.')
#     else:
#         form = FarmerEditForm(instance=farmer)

#     context = {
#         'form': form,
#         'farmer': farmer,
#     }
#     return render(request, 'edit_farmers.html', context)


@login_required
@csrf_protect
def edit_farmer(request, farmer_id):
    farmer = get_object_or_404(Farmer, id=farmer_id)

    if request.method == 'POST':
        form = FarmerEditForm(request.POST, instance=farmer)
        if form.is_valid():
            edited_farmer = form.save(commit=False)
            
            # Check if the number is being changed
            new_number = edited_farmer.number
            if new_number != farmer.number:
                # Ensure no other farmer has the same number
                if Farmer.objects.filter(number=new_number).exists():
                    messages.error(request, f'Farmer number {new_number} already exists.')
                else:
                    # Save the farmer with the new number
                    edited_farmer.save()
                    
                    # Update the sequence of all farmers' numbers
                    farmers = Farmer.objects.all().order_by('id')
                    for index, farmer in enumerate(farmers, start=1):
                        farmer.number = f'{index:03}'
                        farmer.save()

                    messages.success(request, 'Farmer details updated successfully.')
                    return redirect('edit_farmer', farmer_id=farmer.id)  # Redirect with farmer_id
            else:
                # Save the farmer without changing the number
                edited_farmer.save()
                messages.success(request, 'Farmer details updated successfully.')
                return redirect('edit_farmer', farmer_id=farmer.id)  # Redirect with farmer_id
        else:
            messages.error(request, 'Failed to update farmer details. Please correct the errors below.')
    else:
        form = FarmerEditForm(instance=farmer)

    context = {
        'form': form,
        'farmer': farmer,
    }
    return render(request, 'edit_farmer.html', context)



@login_required
@csrf_protect
def add_farmer_with_number(request):
    if request.method == 'POST':
        form = FarmerAddForm(request.POST)
        if form.is_valid():
            new_farmer = form.save(commit=False)
            
            # Ensure the specified number is unique
            if Farmer.objects.filter(number=new_farmer.number).exists():
                messages.error(request, f'Farmer number {new_farmer.number} already exists.')
            else:
                new_farmer.save()
                
                # Update the sequence of all farmers' numbers
                farmers = list(Farmer.objects.all().order_by('id'))
                farmers.sort(key=lambda x: int(x.number))  # Sort farmers by number
                
                for index, farmer in enumerate(farmers):
                    farmer.number = f'{index + 1:03}'  # Ensure the number is 3 digits
                    farmer.save()

                messages.success(request, 'Farmer added successfully.')
                return redirect('all-farmers')
        else:
            messages.error(request, 'Failed to add farmer. Please correct the errors below.')
    else:
        form = FarmerAddForm()

    context = {
        'form': form,
    }
    return render(request, 'addfarmer.html', context)



def admin_edit_requests(request):
    edit_requests = EditRequest.objects.filter(status='Pending')

    return render(request, 'edit_requests.html', {'edit_requests': edit_requests})

def approve_edit_request(request, request_id):
    edit_request = get_object_or_404(EditRequest, pk=request_id)
    
    # Update the corresponding weight entry based on the request
    if edit_request.berry_type == 'cherry':
        cherry_weight = CherryWeight.objects.filter(field__farmer=edit_request.farmer, field__harvest=edit_request.harvest).first()
        if cherry_weight:
            cherry_weight.weight = edit_request.new_weight
            cherry_weight.save()

    elif edit_request.berry_type == 'mbuni':
        mbuni_weight = MbuniWeight.objects.filter(field__farmer=edit_request.farmer, field__harvest=edit_request.harvest).first()
        if mbuni_weight:
            mbuni_weight.weight = edit_request.new_weight
            mbuni_weight.save()

    # Update the edit request status
    edit_request.status = 'Approved'
    edit_request.save()

    messages.success(request, 'Edit request approved successfully.')
    return redirect('admin_edit_requests')

def reject_edit_request(request, request_id):
    edit_request = get_object_or_404(EditRequest, pk=request_id)
    edit_request.status = 'Rejected'
    edit_request.save()

    messages.info(request, 'Edit request rejected.')
    return redirect('admin_edit_requests')