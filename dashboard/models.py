from django.db import models


class Farmer(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=100)
    location = models.TextField()
    id_number = models.CharField(max_length=100)
    berry_weight = models.FloatField(null=True, blank=True)
    
    def __str__(self):
        return self.name