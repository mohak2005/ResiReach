# custom_admin/views.py
from django.db.models import Avg
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from accounts.models import CustomUser
from accounts.models import ServiceProvider
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

# Only staff/superusers can access these views
def is_admin(user):
    return user.is_staff or user.is_superuser


# ------------------------
# ADMIN LOGIN VIEW
# ------------------------
def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(request, username=username, password=password)
        if user is not None and (user.is_staff or user.is_superuser):
            login(request, user)
            return redirect("custom_admin:dashboard")
        else:
            messages.error(request, "Invalid credentials or not authorized.")
    return render(request, "custom_admin/admin_login.html")


# ------------------------
# ADMIN LOGOUT VIEW
# ------------------------
def admin_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("custom_admin:admin_login")


# ------------------------
# ADMIN DASHBOARD VIEW
# ------------------------
@user_passes_test(is_admin, login_url='custom_admin:admin_login')
def admin_dashboard(request):
    # fetch all non-admin users (residents)
    residents = CustomUser.objects.filter(
    is_staff=False,
    is_superuser=False
).exclude(id__in=ServiceProvider.objects.values('user_id'))


    # Prepare a list with their full details
    resident_data = []
    for user in residents:
        # If you are using RegistrationRequest to store full details
        try:
            reg_request = user.registrationrequest  # OneToOneField
            resident_info = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": reg_request.full_name,
                "phone": reg_request.phone,
                "flat_number": reg_request.flat_number,
                "address": reg_request.address,
                "document": reg_request.document.url if reg_request.document else "",
                "is_active": user.is_active,
            }
        except:
            # fallback to CustomUser fields if registrationrequest not found
            resident_info = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "phone": user.phone_number,
                "flat_number": user.flat_number,
                "address": user.address,
                "document": user.document.url if user.document else "",
                "is_active": user.is_active,
            }
        resident_data.append(resident_info)

    context = {
        "total_residents": residents.count(),
        "pending_residents": residents.filter(is_active=False).count(),
        "approved_residents": residents.filter(is_active=True).count(),
        "residents": resident_data,
    }

    return render(request, "custom_admin/admin_dashboard.html", context)



# ------------------------
# APPROVE RESIDENT
# ------------------------
@user_passes_test(is_admin, login_url='custom_admin:admin_login')
def approve_resident(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)

    # Only send email when user is being activated for the first time
    sending_email = not user.is_active  

    user.is_active = True
    user.save()

    # -------------------------
    # SEND EMAIL HERE (NO SIGNALS)
    # -------------------------
    if sending_email:  
        subject = "🎉 Your ResiReach Account Has Been Approved!"
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [user.email]

        context = {
            'full_name': user.full_name,
            'username': user.username,
        }

        html_content = render_to_string('accounts/emails/account_approved.html', context)
        text_content = (
            f"Hello {user.full_name}, your ResiReach resident account has been approved. "
            "You can now log in and start using the platform."
        )

        email = EmailMultiAlternatives(
            subject,
            text_content,
            from_email,
            to_email,
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

    messages.success(request, f"{user.username} has been approved successfully.")
    return redirect("custom_admin:dashboard")



# ------------------------
# REJECT RESIDENT
# ------------------------
@user_passes_test(is_admin, login_url='custom_admin:admin_login')
def reject_resident(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.delete()
    messages.error(request, f"{user.username} has been rejected and removed.")
    return redirect("custom_admin:dashboard")


# ------------------------
# DELETE RESIDENT
# ------------------------
@user_passes_test(is_admin, login_url='custom_admin:admin_login')
def delete_resident(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.delete()
    messages.warning(request, f"{user.username} has been deleted.")
    return redirect("custom_admin:dashboard")

# Promote resident to staff
@user_passes_test(is_admin, login_url='custom_admin:admin_login')
def make_staff(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_staff = True
    user.save()
    messages.success(request, f"{user.username} is now a staff member.")
    return redirect("custom_admin:dashboard")


# Promote resident to superuser
@user_passes_test(is_admin, login_url='custom_admin:admin_login')
def make_superuser(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_superuser = True
    user.is_staff = True  # superuser must also be staff
    user.save()
    messages.success(request, f"{user.username} is now a superuser.")
    return redirect("custom_admin:dashboard")


# Demote superuser/staff to normal resident
@user_passes_test(is_admin, login_url='custom_admin:admin_login')
def demote_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_superuser = False
    user.is_staff = False
    user.save()
    messages.success(request, f"{user.username} is now a regular resident.")
    return redirect("custom_admin:dashboard")



def admin_required(view_func):
    return user_passes_test(lambda u: u.is_superuser)(view_func)


# custom_admin/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from accounts.models import CustomUser, ServiceProvider, ServiceProviderReference
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

# Only staff/superusers can access these views
def is_admin(user):
    return user.is_staff or user.is_superuser


# ------------------------
# ADMIN LOGIN VIEW
# ------------------------
def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(request, username=username, password=password)
        if user is not None and (user.is_staff or user.is_superuser):
            login(request, user)
            return redirect("custom_admin:dashboard")
        else:
            messages.error(request, "Invalid credentials or not authorized.")
    return render(request, "custom_admin/admin_login.html")


# ------------------------
# ADMIN LOGOUT VIEW
# ------------------------
def admin_logout(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("custom_admin:admin_login")


# ------------------------
# ADMIN DASHBOARD VIEW (UPDATED WITH COMPLETE SERVICE PROVIDER DETAILS)
# ------------------------
@user_passes_test(is_admin, login_url='custom_admin:admin_login')
def admin_dashboard(request):
    # fetch all non-admin users (residents) excluding service providers
    residents = CustomUser.objects.filter(
        is_staff=False,
        is_superuser=False
    ).exclude(id__in=ServiceProvider.objects.values('user_id'))

    # Prepare a list with their full details
    resident_data = []
    for user in residents:
        try:
            reg_request = user.registrationrequest  # OneToOneField
            resident_info = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": reg_request.full_name,
                "phone": reg_request.phone,
                "flat_number": reg_request.flat_number,
                "address": reg_request.address,
                "document": reg_request.document.url if reg_request.document else "",
                "is_active": user.is_active,
            }
        except:
            resident_info = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "phone": user.phone_number,
                "flat_number": user.flat_number,
                "address": user.address,
                "document": user.document.url if user.document else "",
                "is_active": user.is_active,
            }
        resident_data.append(resident_info)

    # Service Provider Data
    service_providers = (
    ServiceProvider.objects
    .all()
    .select_related('user')
    .prefetch_related('references')
    .annotate(avg_rating=Avg('feedbacks__rating'))   # ⭐ Add average rating here
)
    
    provider_data = []
    for provider in service_providers:
        provider_data.append({
            "id": provider.id,
            "username": provider.user.username,
            "full_name": provider.full_name,
            "parent_name": provider.parent_name,
            "gender": provider.gender,
            "dob": provider.dob,
            "mobile": provider.mobile,
            "alternate_mobile": provider.alternate_mobile,
            "email": provider.email,
            "profile_photo": provider.profile_photo,
            "address": provider.address,
            "city": provider.city,
            "state": provider.state,
            "pincode": provider.pincode,
            "govt_id_type": provider.govt_id_type,
            "govt_id_number": provider.govt_id_number,
            "govt_id_document": provider.govt_id_document,
            "address_proof": provider.address_proof,
            "service_category": provider.service_category,
            "experience": provider.experience,
            "skills": provider.skills,
            "work_certificate": provider.work_certificate,
            "working_hours": provider.working_hours,
            "service_area": provider.service_area,
            "employment_type": provider.employment_type,
            "business_name": provider.business_name,
            "business_address": provider.business_address,
            "employer_name": provider.employer_name,
            "employer_number": provider.employer_number,
            "company_name": provider.company_name,
            "company_address": provider.company_address,
            "is_verified": provider.is_verified,
            "references": list(provider.references.all()),
            "avg_rating": provider.avg_rating,  # ⭐ Include average rating
        })

    context = {
        "total_residents": residents.count(),
        "pending_residents": residents.filter(is_active=False).count(),
        "approved_residents": residents.filter(is_active=True).count(),
        "residents": resident_data,

        "total_providers": service_providers.count(),
        "pending_providers": service_providers.filter(is_verified=False).count(),
        "approved_providers": service_providers.filter(is_verified=True).count(),
        "service_providers": provider_data,
    }

    return render(request, "custom_admin/admin_dashboard.html", context)



# ------------------------
# RESIDENT ACTIONS
# ------------------------
@user_passes_test(is_admin, login_url='custom_admin:admin_login')
def approve_resident(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_active = True
    user.save()
    messages.success(request, f"{user.username} has been approved successfully.")
    return redirect("custom_admin:dashboard")


@user_passes_test(is_admin, login_url='custom_admin:admin_login')
def reject_resident(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.delete()
    messages.error(request, f"{user.username} has been rejected and removed.")
    return redirect("custom_admin:dashboard")


@user_passes_test(is_admin, login_url='custom_admin:admin_login')
def delete_resident(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.delete()
    messages.warning(request, f"{user.username} has been deleted.")
    return redirect("custom_admin:dashboard")


@user_passes_test(is_admin, login_url='custom_admin:admin_login')
def make_staff(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_staff = True
    user.save()
    messages.success(request, f"{user.username} is now a staff member.")
    return redirect("custom_admin:dashboard")


@user_passes_test(is_admin, login_url='custom_admin:admin_login')
def make_superuser(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_superuser = True
    user.is_staff = True  # superuser must also be staff
    user.save()
    messages.success(request, f"{user.username} is now a superuser.")
    return redirect("custom_admin:dashboard")


@user_passes_test(is_admin, login_url='custom_admin:admin_login')
def demote_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_superuser = False
    user.is_staff = False
    user.save()
    messages.success(request, f"{user.username} is now a regular resident.")
    return redirect("custom_admin:dashboard")


# ------------------------
# SERVICE PROVIDER ACTIONS
# ------------------------

@user_passes_test(is_admin, login_url='custom_admin:admin_login')
def approve_service_provider(request, provider_id):
    provider = get_object_or_404(ServiceProvider, id=provider_id)
    
    # Activate the associated user account
    provider.user.is_active = True
    provider.user.save()
    
    # Verify the service provider
    provider.is_verified = True
    provider.save()
    
    # Send approval email (optional)
    try:
        subject = 'Service Provider Account Approved - ResiReach'
        html_content = render_to_string('custom_admin/emails/service_provider_approved.html', {
            'provider': provider,
        })
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=f"Dear {provider.full_name}, your service provider account has been approved. You can now login and start receiving service requests.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[provider.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
    except Exception as e:
        # Log the error but don't break the approval process
        print(f"Failed to send approval email: {e}")
    
    messages.success(request, f"{provider.full_name} has been approved successfully. Notification email sent.")
    return redirect("custom_admin:dashboard")


@user_passes_test(is_admin, login_url='custom_admin:admin_login')
def reject_service_provider(request, provider_id):
    provider = get_object_or_404(ServiceProvider, id=provider_id)
    provider_name = provider.full_name
    user_email = provider.email
    
    # Send rejection email before deletion (optional)
    try:
        subject = 'Service Provider Application Status - ResiReach'
        html_content = render_to_string('custom_admin/emails/service_provider_rejected.html', {
            'provider_name': provider_name,
        })
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=f"Dear {provider_name}, after careful review, we regret to inform you that your service provider application has not been approved at this time.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user_email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
    except Exception as e:
        # Log the error but don't break the rejection process
        print(f"Failed to send rejection email: {e}")
    
    # Delete the service provider and associated user
    user = provider.user
    provider.delete()
    user.delete()
    
    messages.error(request, f"{provider_name} has been rejected and removed. Notification email sent.")
    return redirect("custom_admin:dashboard")


@user_passes_test(is_admin, login_url='custom_admin:admin_login')
def delete_service_provider(request, provider_id):
    provider = get_object_or_404(ServiceProvider, id=provider_id)
    provider_name = provider.full_name
    
    # Delete the service provider and associated user
    user = provider.user
    provider.delete()
    user.delete()
    
    messages.warning(request, f"{provider_name} has been permanently deleted.")
    return redirect("custom_admin:dashboard")


def admin_required(view_func):
    return user_passes_test(lambda u: u.is_superuser)(view_func)