from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Farmer




class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class RegisterForm(forms.ModelForm):
    class Meta:
        model = Farmer
        fields = ['name', 'phone', 'location', 'id_number']

class FarmerWeightForm(forms.Form):
    Farmer_name = forms.CharField(label="Farmer's name", max_length=100)
    berry_weight = forms.FloatField(label="Coffe berries weight (kg)")

    def clean_Farmer(self):
        farmer_name = self.cleaned_data.get('Farmer')
        if not Farmer.objects.filter(name=farmer_name).exists():
            raise forms.ValidationError('Farmer does not exist')
        return farmer_name