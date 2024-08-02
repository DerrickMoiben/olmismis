from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from dashboard.models import Farmer, Harvest

class EditRequest(models.Model):
    farmer = models.ForeignKey('dashboard.Farmer', on_delete=models.CASCADE)
    berry_type = models.CharField(max_length=10)  # 'cherry' or 'mbuni'
    current_weight = models.FloatField()
    new_weight = models.FloatField()
    harvest = models.ForeignKey('dashboard.Harvest', on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending')
    cashier = models.ForeignKey(User, on_delete=models.CASCADE)  # Assuming cashiers are users

    def __str__(self):
        return f"{self.farmer.name} - {self.berry_type} Edit Request"