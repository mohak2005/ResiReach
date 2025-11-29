# accounts/urls.py
from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('about/', views.about, name='about'),
    path('committee/', views.committee, name='committee'),
    path('services/', views.services, name='services'),
    path('profile/', views.profile, name='profile'),
    path("signup/service-provider/", views.signup_service_provider, name="signup_service_provider"),
    path("login/service-provider/", views.login_service_provider, name="login_service_provider"),
    path("dashboard/service-provider/", views.service_provider_dashboard, name="provider_dashboard"),
    path("about/service-provider/", views.about_service_provider, name="about_service_provider"),
    path("committee/service-provider/", views.committee_service_provider, name="committee_service_provider"),
    path("logout/service-provider/", views.logout_service_provider, name="logout_service_provider"),
]
