from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

from .models import CustomUser, ServiceProvider, ServiceProviderReference


# -----------------------------
# 1️⃣ CUSTOM USER ADMIN
# -----------------------------
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'full_name', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'phone_number', 'flat_number', 'address', 'document')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'full_name', 'password1', 'password2', 'is_active', 'is_staff'),
        }),
    )
    search_fields = ('username', 'email', 'full_name')
    ordering = ('username',)


admin.site.register(CustomUser, CustomUserAdmin)


# -----------------------------
# 2️⃣ INLINE FOR REFERENCES
# -----------------------------
class ServiceProviderReferenceInline(admin.TabularInline):
    model = ServiceProviderReference
    extra = 0
    

# -----------------------------
# 3️⃣ SERVICE PROVIDER ADMIN
# -----------------------------
@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'service_category', 'is_verified')
    list_filter = ('is_verified', 'service_category')
    search_fields = ('full_name', 'user__username')
    inlines = [ServiceProviderReferenceInline]

    def save_model(self, request, obj, form, change):
        """
        Send approval email when admin sets is_verified=True.
        """
        if change:
            old_obj = ServiceProvider.objects.get(pk=obj.pk)
            # Check if admin just approved the provider
            if not old_obj.is_verified and obj.is_verified:
                user = obj.user  # the linked CustomUser

                # ✅ Prepare email context
                context = {
                    'full_name': user.full_name,
                    'service_category': obj.service_category,
                    'user': user.username,
                }

                # ✅ Render HTML and plain text content
                subject = "🎉 Your ResiReach Account Has Been Approved!"
                html_content = render_to_string(
                    'accounts/emails/approval_email.html',  # your HTML email template
                    context
                )
                text_content = (
                    f"Hello {user.full_name}, your account has been approved. "
                    f"You can now log in and provide {obj.service_category} services."
                )

                # ✅ Send email
                email = EmailMultiAlternatives(
                    subject,
                    text_content,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                )
                email.attach_alternative(html_content, "text/html")
                email.send()

        super().save_model(request, obj, form, change)

# -----------------------------
# 4️⃣ REFERENCE ADMIN (OPTIONAL)
# -----------------------------
@admin.register(ServiceProviderReference)
class ServiceProviderReferenceAdmin(admin.ModelAdmin):
    list_display = ('service_provider', 'customer_name', 'customer_contact')
    search_fields = ('customer_name', 'service_provider__user__username')
