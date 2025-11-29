# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, RegistrationRequest

class ResidentSignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    full_name = forms.CharField(max_length=100)
    phone_number = forms.CharField(max_length=15)
    flat_number = forms.CharField(max_length=10)
    address = forms.CharField(widget=forms.Textarea)
    document = forms.FileField(required=True)

    class Meta:
        model = CustomUser
        fields = [
            "username", "email", "password1", "password2",
            "full_name", "phone_number", "flat_number", "address", "document",
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.full_name = self.cleaned_data['full_name']
        user.phone_number = self.cleaned_data['phone_number']
        user.flat_number = self.cleaned_data['flat_number']
        user.address = self.cleaned_data['address']
        user.document = self.cleaned_data['document']
        user.is_active = False  # ❌ not active until admin approves
        
        if commit:
            user.save()
            
            # Create registration request
            RegistrationRequest.objects.create(
                user=user,
                full_name=user.full_name,
                phone=user.phone_number,
                flat_number=user.flat_number,
                address=user.address,
                document=user.document
            )
            
        return user


from django import forms
from django.contrib.auth.models import User
from .models import ServiceProvider
from .models import ServiceProvider, ServiceProviderReference

class ServiceProviderRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    EMPLOYMENT_CHOICES = [
        ('freelancer', 'Freelancer / Independent'),
        ('contractor', 'Contractor'),
        ('own_shop', 'Own Shop'),
    ]

    employment_type = forms.ChoiceField(
        choices=EMPLOYMENT_CHOICES,
        widget=forms.RadioSelect,
        required=True
    )
    
    # Reference fields - these will be dynamically added in the view
    reference_count = forms.IntegerField(widget=forms.HiddenInput(), initial=1)

    class Meta:
        model = ServiceProvider
        exclude = ['user', 'is_verified']
        
    def __init__(self, *args, **kwargs):
        reference_data = kwargs.pop('reference_data', None)
        super().__init__(*args, **kwargs)
        
        # Add dynamic reference fields based on submitted data
        if reference_data:
            for i in range(1, reference_data + 1):
                self.fields[f'customer_name_{i}'] = forms.CharField(
                    required=True, 
                    label=f'Customer Name #{i}'
                )
                self.fields[f'customer_contact_{i}'] = forms.CharField(
                    required=True,
                    label=f'Customer Contact #{i}'
                )
                self.fields[f'customer_address_{i}'] = forms.CharField(
                    required=True,
                    label=f'Customer Address #{i}'
                )
                self.fields[f'service_description_{i}'] = forms.CharField(
                    required=True,
                    label=f'Service Description #{i}'
                )


class ServiceProviderForm(forms.ModelForm):
    class Meta:
        model = ServiceProvider
        exclude = ['user', 'is_verified']

class ServiceProviderReferenceForm(forms.ModelForm):
    class Meta:
        model = ServiceProviderReference
        fields = ['customer_name', 'customer_contact', 'customer_address', 'service_description']




