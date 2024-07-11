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

    def __str__(self):
        return self.name

class Field(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE)
    field_name = models.CharField(max_length=100)

    def __str__(self):
        return self.field_name
    
class CoffeeBerries(models.Model):
    BERRY_TYPES = [
        ('cherry', 'Cherry'),
        ('mbuni', 'Mbuni'),
    ]
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    weight = models.FloatField()
    berry_type = models.CharField(max_length=10, choices=BERRY_TYPES, default=True)