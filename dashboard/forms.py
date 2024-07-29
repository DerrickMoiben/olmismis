from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Farmer, CherryWeight, MbuniWeight




class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)


class FarmerForm(forms.ModelForm):
    AGREEMENT_CHOICES = [
        ('None', 'None'),
        ('Kapkures  AGC', 'Kapkures AGC'),
        ('Blue Hills AGC', 'Blue Hills AGC'),
    ]
    
    agreement = forms.ChoiceField(choices=AGREEMENT_CHOICES, required=True)
    class Meta:
        model = Farmer
        fields = ['name', 'phone', 'location', 'id_number', 'agreement']

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        phone = cleaned_data.get('phone')


        if Farmer.objects.filter(name=name, phone=phone).exists():
            raise forms.ValidationError("The  farmer already registered.")
        return cleaned_data

class CoffeeBerriesForm(forms.Form):
    farmer_number = forms.CharField(label="Farmer's number", max_length=100)
    berry_type = forms.ChoiceField(label="Berry Type", choices=[('cherry', 'Cherry'), ('mbuni', 'Mbuni')])
    weight = forms.FloatField(label="Coffee berries weight (kg)")

    
class AnnouncementsForm(forms.Form):
    message = forms.CharField(
        label='Message',
        widget=forms.Textarea(
            attrs={
                'rows': 5,
                'placeholder': 'Enter your announcement message here...'
            }
        ),
        required=True
    )

from django import forms
from .models import Season

class SeasonForm(forms.ModelForm):
    class Meta:
        model = Season
        fields = ['name', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'required': False}),
        }


from .models import Harvest

class HarvestForm(forms.ModelForm):
    class Meta:
        model = Harvest
        fields = ['name', 'season', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'required': False}),
        }