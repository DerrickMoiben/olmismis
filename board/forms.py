
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from dashboard.models import Farmer


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username']

class LoginboardForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

class FarmerEditForm(forms.ModelForm):
    class Meta:
        model = Farmer
        fields = ['name', 'phone', 'location', 'id_number']
