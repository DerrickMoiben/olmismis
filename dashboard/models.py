from django.db import models


#class Farmer(models.Model):
    ###location = models.TextField()
   #id_number = models.CharField(max_length=100)
    #berry_weight = models.FloatField(null=True, blank=True)
    
    #def __str__(self):
       # return self.name
class Farmer(models.Model):
    id_number = models.CharField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    location = models.TextField()

    def __str__(self):
        return self.name
    
class Field(models.Model):
    farmer = models.ForeignKey(Farmer, on_delete=models.CASCADE)
    field_name = models.CharField(max_length=100)

    def __str__(self):
        return self.field_name
    
class CoffeeBerries(models.Model):
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    weight = models.FloatField(null=False, blank=False)
    