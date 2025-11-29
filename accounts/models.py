from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings


# -----------------------------
# 1️⃣ Custom User Model
# -----------------------------
class CustomUser(AbstractUser):
    full_name = models.CharField(max_length=100, default='Not Provided')
    phone_number = models.CharField(max_length=20, default='Not Provided')
    flat_number = models.CharField(max_length=10, default='Not Provided')
    address = models.TextField(default='Not Provided')
    document = models.FileField(upload_to='documents/', null=True, blank=True)

    def __str__(self):
        return self.username


class ResidentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    flat_number = models.CharField(max_length=10)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    joined_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.full_name} ({self.user.email})"


class RegistrationRequest(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    flat_number = models.CharField(max_length=20)
    address = models.TextField()
    document = models.FileField(upload_to='documents/')
    submitted_at = models.DateTimeField(default=timezone.now)
    reviewed = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)

    def __str__(self):
        return f"RegistrationRequest({self.user.username})"


class ServiceProvider(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    parent_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=20)
    dob = models.DateField()
    mobile = models.CharField(max_length=15)
    alternate_mobile = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField()
    profile_photo = models.ImageField(upload_to='service_providers/photos/')
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)

    govt_id_type = models.CharField(max_length=50)
    govt_id_number = models.CharField(max_length=50)
    govt_id_document = models.FileField(upload_to='service_providers/ids/')
    address_proof = models.FileField(upload_to='service_providers/address_proofs/')

    service_category = models.CharField(max_length=100)
    experience = models.PositiveIntegerField()
    skills = models.TextField()
    work_certificate = models.FileField(upload_to='service_providers/certificates/', blank=True, null=True)
    working_hours = models.CharField(max_length=100)
    service_area = models.CharField(max_length=200)

    employment_type = models.CharField(max_length=50)
    business_name = models.CharField(max_length=100, blank=True, null=True)
    business_address = models.CharField(max_length=200, blank=True, null=True)
    employer_name = models.CharField(max_length=100, blank=True, null=True)
    employer_number = models.CharField(max_length=15, blank=True, null=True)
    company_name = models.CharField(max_length=100, blank=True, null=True)
    company_address = models.CharField(max_length=200, blank=True, null=True)

    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.full_name} ({self.user.username})"


class ServiceProviderReference(models.Model):
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='references')
    customer_name = models.CharField(max_length=100)
    customer_contact = models.CharField(max_length=15)
    customer_address = models.CharField(max_length=200)
    service_description = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.customer_name} - {self.service_provider.full_name}"

