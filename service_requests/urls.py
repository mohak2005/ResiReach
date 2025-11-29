from django.urls import path
from . import views

app_name = 'service_requests'

urlpatterns = [
    path('submit/<int:category_id>/', views.submit_service_request, name='submit_service_request'),
    path('resident/dashboard/', views.resident_dashboard, name='resident_dashboard'),
    path('resident/request/<int:pk>/', views.resident_request_detail, name='resident_request_detail'),
    path('resident/request/<int:request_id>/select/<int:response_id>/', views.resident_select_provider, name='resident_select_provider'),
    path('resident/request/<int:request_id>/accept_completion/', views.resident_accept_completion, name='resident_accept_completion'),
    path('resident/request/<int:request_id>/feedback/', views.submit_feedback, name='submit_feedback'),

    path('provider/dashboard/', views.provider_dashboard, name='provider_dashboard'),
    path('provider/request/<int:request_id>/respond/', views.provider_response, name='provider_response'),
    path('provider/request/<int:request_id>/mark_completed/', views.provider_mark_completed, name='provider_mark_completed'),
]
