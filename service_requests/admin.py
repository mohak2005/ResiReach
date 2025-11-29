from django.contrib import admin
from .models import ServiceCategory, ServiceRequest, ProviderResponse, ServiceFeedback


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'resident', 'status', 'created_at', 'confirmed_provider')
    list_filter = ('status', 'category')


@admin.register(ProviderResponse)
class ProviderResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'service_request', 'provider', 'action', 'created_at', 'is_selected_by_resident')
    list_filter = ('action', 'is_selected_by_resident')


@admin.register(ServiceFeedback)
class ServiceFeedbackAdmin(admin.ModelAdmin):
    # FIXED: 'request' replaced with 'service_request'
    list_display = ('id', 'service_request', 'provider', 'rating', 'created_at')
    list_filter = ('rating',)
