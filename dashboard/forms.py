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
        ('Kapkures AGC', 'Kapkures AGC'),
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


class CashierEditForm(forms.Form):
    farmer_number = forms.CharField(max_length=100, label='Farmer Number')
    berry_type = forms.ChoiceField(choices=[('cherry', 'Cherry'), ('mbuni', 'Mbuni')], label='Berry Type')
    current_weight = forms.FloatField(label='Current Weight', required=False)
    new_weight = forms.FloatField(label='New Weight')

    def __init__(self, *args, **kwargs):
        # Extract the selected_harvest_id from kwargs
        self.selected_harvest_id = kwargs.pop('selected_harvest_id', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        farmer_number = cleaned_data.get('farmer_number')
        berry_type = cleaned_data.get('berry_type')

        # Validate that the farmer exists
        try:
            farmer = Farmer.objects.get(number=farmer_number)
            cleaned_data['farmer'] = farmer
        except Farmer.DoesNotExist:
            raise forms.ValidationError("Farmer with this number does not exist.")

        # Validate that the selected harvest ID is available
        if self.selected_harvest_id is None:
            raise forms.ValidationError("No harvest selected. Please select a harvest.")

        # Validate current weight based on berry type and harvest
        if berry_type == 'cherry':
            cherry_weight = CherryWeight.objects.filter(field__farmer=cleaned_data['farmer'], field__harvest_id=self.selected_harvest_id).first()
            if cherry_weight:
                cleaned_data['current_weight'] = cherry_weight.weight
            else:
                raise forms.ValidationError("No cherry weight found for this farmer in the selected harvest.")
        elif berry_type == 'mbuni':
            mbuni_weight = MbuniWeight.objects.filter(field__farmer=cleaned_data['farmer'], field__harvest_id=self.selected_harvest_id).first()
            if mbuni_weight:
                cleaned_data['current_weight'] = mbuni_weight.weight
            else:
                raise forms.ValidationError("No mbuni weight found for this farmer in the selected harvest.")

        return cleaned_data