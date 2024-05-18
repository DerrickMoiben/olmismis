from django.shortcuts import render, redirect
from .models import Farmer
from .forms import FarmerForm



def farmers(request):
    farmers = Farmer.objects.all()
    return render(request, 'farmers/farmers.html', {'farmers': farmers})


def farmer_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        id_number = request.POST.get('id_number')
        berry_weight = request.POST.get('berry_weight')
        
        farmer = Farmer(name=name, phone=phone, address=address, id_number=id_number, berry_weight=berry_weight)
        farmer.save()
        return redirect('farmers')
    return render(request, 'farmers/farmer_create.html')

def farmer_update(request, id):
    farmer = Farmer.objects.get(id=id)
    if request.method == 'POST':
        farmer.name = request.POST.get('name')
        farmer.phone = request.POST.get('phone')
        farmer.address = request.POST.get('address')
        farmer.id_number = request.POST.get('id_number')
        farmer.berry_weight = request.POST.get('berry_weight')
        farmer.save()
        return redirect('farmers')
    return render(request, 'farmers/farmer_update.html', {'farmer': farmer})


def farmer_delete(request, id):
    farmer = Farmer.objects.get(id=id)
    farmer.delete()
    return redirect('farmers')