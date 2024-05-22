from typing import Any
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Farmer, CoffeeBerries




class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class FarmerForm(forms.ModelForm):
    class Meta:
        model = Farmer
        fields = ['name', 'phone', 'location']

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        phone = cleaned_data.get('phone')

        if Farmer.objects.filter(name=name, phone=phone).exists():
            raise forms.ValidationError("The  farmer already registered.")
        return cleaned_data

class CoffeeBerriesForm(forms.Form):
    farmer_name = forms.CharField(label="Farmer's name", max_length=100)
    weight = forms.FloatField(label="Coffee berries weight (kg)", initial=0.0)