from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from .models import CustomUser

# --- Signup Confirmation Email ---
@receiver(post_save, sender=CustomUser)
def send_signup_confirmation(sender, instance, created, **kwargs):
    if created:
        subject = "✅ Your ResiReach Signup Request Received"
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [instance.email]
        context = {
            'full_name': instance.full_name,
            'username': instance.username,
        }
        html_content = render_to_string('accounts/emails/signup_confirmation.html', context)
        text_content = f"Hello {instance.full_name}, your signup request has been received and is pending admin approval."

        email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        email.attach_alternative(html_content, "text/html")
        email.send()

# --- Account Approved Email ---
@receiver(post_save, sender=CustomUser)
def send_account_approved_email(sender, instance, created, **kwargs):
    if not created and instance.is_active and not instance.is_superuser:
        subject = "🎉 Your ResiReach Account Has Been Approved!"
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [instance.email]
        context = {
            'full_name': instance.full_name,
            'username': instance.username,
        }
        html_content = render_to_string('accounts/emails/account_approved.html', context)
        text_content = f"Hello {instance.full_name}, your account has been approved. You can now log in to ResiReach."

        email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        email.attach_alternative(html_content, "text/html")
        email.send()


