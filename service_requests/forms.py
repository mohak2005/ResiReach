# forms.py
from django import forms
from .models import ServiceRequest, ProviderResponse, ServiceFeedback

class ServiceRequestForm(forms.ModelForm):
    service_details = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4}),
        label='Service Details / Special Requirements'
    )
    
    class Meta:
        model = ServiceRequest
        fields = [
            'first_name', 'last_name', 'phone', 'email', 
            'apartment_details', 'preferred_date', 'preferred_time'
        ]
        widgets = {
            'preferred_date': forms.DateInput(attrs={'type': 'date'}),
            'preferred_time': forms.TimeInput(attrs={'type': 'time'}),
        }

class ProviderResponseForm(forms.ModelForm):
    class Meta:
        model = ProviderResponse
        fields = ['action', 'message', 'proposed_date', 'proposed_time']
        widgets = {
            'proposed_date': forms.DateInput(attrs={'type': 'date'}),
            'proposed_time': forms.TimeInput(attrs={'type': 'time'}),
            'message': forms.Textarea(attrs={'rows': 4}),
        }

class ServiceFeedbackForm(forms.ModelForm):
    class Meta:
        model = ServiceFeedback
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'rows': 4}),
        }