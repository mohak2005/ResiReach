from django.urls import path
from . import views

app_name = 'custom_admin'

urlpatterns = [
    path('login/', views.admin_login, name='admin_login'),
    path('logout/', views.admin_logout, name='admin_logout'),
    path('dashboard/', views.admin_dashboard, name='dashboard'),
    path('resident/<int:user_id>/approve/', views.approve_resident, name='approve_resident'),
    path('resident/<int:user_id>/reject/', views.reject_resident, name='reject_resident'),
    path('resident/<int:user_id>/delete/', views.delete_resident, name='delete_resident'),
    path('resident/<int:user_id>/make_staff/', views.make_staff, name='make_staff'),
    path('resident/<int:user_id>/make_superuser/', views.make_superuser, name='make_superuser'),
    path('resident/<int:user_id>/demote/', views.demote_user, name='demote_user'),
    path('approve-service-provider/<int:provider_id>/', views.approve_service_provider, name='approve_service_provider'),
    path('reject-service-provider/<int:provider_id>/', views.reject_service_provider, name='reject_service_provider'),
    path('delete-service-provider/<int:provider_id>/', views.delete_service_provider, name='delete_service_provider'),
]

