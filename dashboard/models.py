# from random import choices
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Farmer(models.Model):
    number = models.CharField(max_length=100, null=True, blank=True)
    id_number = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    location = models.CharField(max_length=100)
    is_number = models.BooleanField(default=False)
    agreement = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name

class Field(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE)
    field_name = models.CharField(max_length=100)
    harvest = models.ForeignKey('Harvest', on_delete=models.CASCADE, null=True, blank=True)  # Add this line

    def __str__(self):
        return self.field_name
    

class CherryWeight(models.Model):
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    weight = models.FloatField()

    def __str__(self):
        return f"{self.field} - Cherry: {self.weight}kg"

class MbuniWeight(models.Model):
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    weight = models.FloatField()

    def __str__(self):
        return f"{self.field} - Mbuni: {self.weight}kg"
    

class Season(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name
class Harvest(models.Model):
    name = models.CharField(max_length=100, default='Harvest')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Harvest from {self.start_date} to {self.end_date or 'Ongoing'} in {self.season.name}"

from django.contrib.auth.models import User
from .models import Harvest

class UserSelectedHarvest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    harvest = models.ForeignKey(Harvest, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.harvest}"

class Payment(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE)
    harvest = models.ForeignKey(Harvest, on_delete=models.CASCADE)
    church = models.CharField(max_length=1, null=True)  # Allow null for no agreement
    berry_type = models.CharField(max_length=10)  # 'cherry' or 'mbuni'
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Total amount before deduction
    amount_received = models.DecimalField(max_digits=10, decimal_places=2)  # Amount after deduction
    price_per_kilo = models.DecimalField(max_digits=10, decimal_places=2)  # Price per kilo for the transaction
    payment_number = models.CharField(max_length=200,  default='Unamed Payment')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.farmer.name} - {self.amount} (Harvest: {self.harvest.name}, Church: {self.church})"
    
class NewPayment(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE)
    harvest = models.ForeignKey(Harvest, on_delete=models.CASCADE)
    church = models.CharField(max_length=1, null=True)  # Allow null for no agreement
    berry_type = models.CharField(max_length=10)  # 'cherry' or 'mbuni'
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Total amount before deduction
    amount_received = models.DecimalField(max_digits=10, decimal_places=2)  # Amount after deduction
    price_per_kilo = models.DecimalField(max_digits=10, decimal_places=2)  # Price per kilo for the transaction
    payment_number = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.farmer.name} - {self.amount} (Harvest: {self.harvest.name}, Church: {self.church})"