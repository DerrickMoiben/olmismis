from django import forms

from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from farmers.models import Farmer

class FarmerForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
