from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth import get_user_model
from .models import CustomUser, ServiceProvider, ServiceProviderReference
from .forms import ResidentSignupForm, ServiceProviderRegistrationForm

User = get_user_model()

# -------------------------------
# 1️⃣ RESIDENT SIGNUP
# -------------------------------
def signup_view(request):
    if request.method == "POST":
        form = ResidentSignupForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Account created successfully! Please wait for admin approval.")
            return redirect("accounts:login")
        else:
            print("Form errors:", form.errors)  # Debugging
            messages.error(request, "Please correct the errors below.")
    else:
        form = ResidentSignupForm()
    return render(request, "accounts/signup.html", {"form": form})


# -------------------------------
# 2️⃣ RESIDENT LOGIN
# -------------------------------
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        if not username or not password:
            messages.error(request, "Please enter both username and password.")
            return redirect("accounts:login")

        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            user = None

        if user and not user.is_active:
            if user.check_password(password):
                messages.error(request, "Your account is not approved yet. Please wait for admin approval.")
                return redirect("accounts:login")
            else:
                messages.error(request, "Invalid username or password.")
                return redirect("accounts:login")

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_active:
            login(request, user)
            return redirect("accounts:dashboard")
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, "accounts/login.html")


# -------------------------------
# 3️⃣ RESIDENT DASHBOARD
# -------------------------------
@login_required(login_url='accounts:login')
def dashboard(request):
    return render(request, 'accounts/dashboard.html', {'user': request.user})


# -------------------------------
# 4️⃣ LOGOUT
# -------------------------------
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('accounts:login')


# -------------------------------
# 5️⃣ STATIC PAGES
# -------------------------------
@login_required(login_url='accounts:login')
def about(request):
    return render(request, 'accounts/about.html')

@login_required(login_url='accounts:login')
def committee(request):
    return render(request, 'accounts/committee.html')

@login_required(login_url='accounts:login')
def services(request):
    return render(request, 'accounts/services.html')

@login_required(login_url='accounts:login')
def profile(request):
    return render(request, 'accounts/profile.html', {'user': request.user})


# -------------------------------
# 6️⃣ SERVICE PROVIDER SIGNUP
# _____________________________
def signup_service_provider(request):
    if request.method == 'POST':
        form = ServiceProviderRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data.get('email', '')
            password = form.cleaned_data['password']

            # ✅ Check if username already exists
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already taken. Please choose another.")
                return redirect('accounts:signup_service_provider')

            # ✅ Create new user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                full_name=form.cleaned_data.get('full_name', ''),
                phone_number=form.cleaned_data.get('mobile', ''),
                address=form.cleaned_data.get('address', ''),
                is_active=False  # mark inactive until admin approval
            )

            # ✅ Create provider profile
            provider = form.save(commit=False)
            provider.user = user
            provider.save()

            # ✅ Save references - FIXED VERSION
            reference_count = int(request.POST.get('reference_count', 1))

            for i in range(1, reference_count + 1):
                customer_name = request.POST.get(f'customer_name_{i}', '').strip()
                customer_contact = request.POST.get(f'customer_contact_{i}', '').strip()
                customer_address = request.POST.get(f'customer_address_{i}', '').strip()
                service_description = request.POST.get(f'service_provided_{i}', '').strip()
                
                if customer_name and customer_contact:
                    ServiceProviderReference.objects.create(
                        service_provider=provider,
                        customer_name=customer_name,
                        customer_contact=customer_contact,
                        customer_address=customer_address,
                        service_description=service_description,
                    )

            # ✅ Send registration email
            context = {
                'full_name': user.full_name,
                'service_category': provider.service_category,
                'user': user.username,
            }
            subject = "🎉 Thank you for registering on ResiReach"
            html_content = render_to_string('accounts/emails/registration_email.html', {'user': user, 'provider': provider})
            text_content = "Thank you for registering. Your account is pending admin approval."

            email = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [user.email])
            email.attach_alternative(html_content, "text/html")
            email.send()

            messages.success(request, "Registration successful! Please wait for admin verification.")
            return redirect('accounts:login_service_provider')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ServiceProviderRegistrationForm()

    return render(request, 'accounts/signup_service_provider.html', {'form': form})



# -------------------------------
# 7️⃣ SERVICE PROVIDER LOGIN
# -------------------------------
def login_service_provider(request):
    """
    Handles login for service providers.
    Checks username, password, and verification status.
    """
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if not username or not password:
            messages.error(request, "Please enter both username and password.")
            return redirect('accounts:login_service_provider')

        user = authenticate(request, username=username, password=password)

        if user:
            # Ensure the user is a service provider
            try:
                provider = ServiceProvider.objects.get(user=user)
            except ServiceProvider.DoesNotExist:
                messages.error(request, "No service provider account linked to this user.")
                return redirect('accounts:login_service_provider')

            if provider.is_verified:
                login(request, user)
                return redirect('accounts:provider_dashboard')
                messages.success(request, f"Welcome back, {user.username}!")
            else:
                messages.warning(request, "Your account is pending admin verification.")
                return render(request, 'accounts/service_provider_login.html')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'accounts/service_provider_login.html')


# -------------------------------
# 8️⃣ SERVICE PROVIDER DASHBOARD
# -------------------------------


@login_required
def service_provider_dashboard(request):
    try:
        provider = ServiceProvider.objects.get(user=request.user)
    except ServiceProvider.DoesNotExist:
        messages.error(request, "Service provider profile not found.")
        return redirect('accounts:login_service_provider')

    return render(request, 'accounts/service_provider_dashboard.html', {'provider': provider})

@login_required
def about_service_provider(request):
    return render(request, 'accounts/provider_about.html')

@login_required
def committee_service_provider(request):
    return render(request, 'accounts/provider_committee.html')

def logout_service_provider(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('accounts:login_service_provider')


