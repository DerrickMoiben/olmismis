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