from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from django.http import HttpResponseForbidden, Http404

from accounts.models import ServiceProvider
from .models import ServiceCategory, ServiceRequest, ProviderResponse, ServiceFeedback

from django.utils.dateparse import parse_date, parse_time


# ---------------------------------------------------------
# 1) SUBMIT SERVICE REQUEST  (RESIDENT)
# ---------------------------------------------------------
@login_required
def submit_service_request(request, category_id):
    category = get_object_or_404(ServiceCategory, pk=category_id)

    if request.method == "POST":
        first_name = request.POST.get('first_name') or request.user.first_name
        last_name = request.POST.get('last_name') or request.user.last_name
        phone = request.POST.get('phone')
        email = request.POST.get('email') or request.user.email
        apartment_details = request.POST.get('apartment_details')
        preferred_date = request.POST.get('preferred_date')
        preferred_time = request.POST.get('preferred_time')
        details = request.POST.get('service_details') or ''

        pref_date = parse_date(preferred_date) if preferred_date else None

        try:
            pref_time = parse_time(preferred_time)
        except Exception:
            pref_time = None

        # Create Service Request
        sr = ServiceRequest.objects.create(
            resident=request.user,
            category=category,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            email=email,
            apartment_details=apartment_details,
            preferred_date=pref_date,
            preferred_time=pref_time,
            details=details,
            status=ServiceRequest.STATUS_PENDING,
        )

        # ---------- Email to Resident ----------
        subject = f"Service request received — {category.name} (Request #{sr.pk})"
        context = {'user': request.user, 'service_request': sr, 'category': category}
        html_message = render_to_string('service_requests/emails/resident_request_received.html', context)

        email_msg = EmailMultiAlternatives(
            subject=subject,
            body="Please view this in an HTML-compatible email app.",
            to=[email]
        )
        email_msg.attach_alternative(html_message, "text/html")
        email_msg.send()

        # ======================================================
        #  PROVIDER MATCHING
        # ======================================================
        base_cat = category.name.split('/')[0].strip().lower()

        providers = ServiceProvider.objects.filter(
            service_category__icontains=base_cat
        )

        if not providers.exists():
            norm = category.name.lower().replace("/", "").replace(" ", "")
            providers = ServiceProvider.objects.filter(
                service_category__icontains=norm
            )

        # ---------- Notify Providers ----------
        for prov in providers:
            prov_ctx = {
                'provider': prov,
                'service_request': sr,
                'category': category,
            }
            prov_subject = f"New service request: {category.name} — Request #{sr.pk}"
            prov_html = render_to_string('service_requests/emails/provider_new_request.html', prov_ctx)

            email_msg = EmailMultiAlternatives(
                subject=prov_subject,
                body="Please view this in an HTML-compatible email app.",
                to=[prov.email]
            )
            email_msg.attach_alternative(prov_html, "text/html")
            email_msg.send()

        return redirect('service_requests:resident_dashboard')

    return render(request, 'service_requests/submit_request.html', {'category': category})



# ---------------------------------------------------------
# 2) RESIDENT DASHBOARD
# ---------------------------------------------------------
@login_required
def resident_dashboard(request):
    requests = ServiceRequest.objects.filter(resident=request.user).order_by('-created_at')
    return render(request, 'service_requests/resident_dashboard.html', {'requests': requests})



# ---------------------------------------------------------
# 3) RESIDENT REQUEST DETAIL
# ---------------------------------------------------------
@login_required
def resident_request_detail(request, pk):
    sr = get_object_or_404(ServiceRequest, pk=pk)

    if sr.resident != request.user:
        return HttpResponseForbidden("You cannot view this request.")

    responses = sr.provider_responses.select_related('provider__user').all()
    return render(request, 'service_requests/resident_request_detail.html', {'sr': sr, 'responses': responses})



# ---------------------------------------------------------
# 4) PROVIDER DASHBOARD
# ---------------------------------------------------------
@login_required
def provider_dashboard(request):
    try:
        provider = request.user.serviceprovider
    except ServiceProvider.DoesNotExist:
        return HttpResponseForbidden("You are not a service provider.")

    incoming = ServiceRequest.objects.filter(
        category__name__icontains=provider.service_category.lower()
    )

    return render(request, 'service_requests/provider_dashboard.html', {
        'provider': provider,
        'incoming': incoming
    })



# ---------------------------------------------------------
# 5) PROVIDER RESPONSE
# ---------------------------------------------------------
@login_required
def provider_response(request, request_id):
    sr = get_object_or_404(ServiceRequest, pk=request_id)

    try:
        provider = request.user.serviceprovider
    except ServiceProvider.DoesNotExist:
        return HttpResponseForbidden("You are not a service provider.")

    existing = ProviderResponse.objects.filter(service_request=sr, provider=provider).first()

    if request.method == "POST":
        action = request.POST.get('action')
        message_text = request.POST.get('message', '')
        proposed_date = request.POST.get('proposed_date') or None
        proposed_time = request.POST.get('proposed_time') or None

        if existing:
            pr = existing
            pr.action = action
            pr.message = message_text
            pr.proposed_date = proposed_date
            pr.proposed_time = proposed_time
            pr.created_at = timezone.now()
            pr.save()
        else:
            pr = ProviderResponse.objects.create(
                service_request=sr,
                provider=provider,
                action=action,
                message=message_text,
                proposed_date=proposed_date,
                proposed_time=proposed_time,
            )

        sr.has_provider_responses = True
        sr.set_status(ServiceRequest.STATUS_PROVIDER_RESPONSES)

        # Email resident
        subject = f"Provider response for your request #{sr.pk}"
        ctx = {'resident': sr.resident, 'service_request': sr, 'provider': provider, 'response': pr}
        html_message = render_to_string('service_requests/emails/resident_provider_response.html', ctx)

        email_msg = EmailMultiAlternatives(
            subject=subject,
            body="Please view this message in an HTML-compatible mail app.",
            to=[sr.email]
        )
        email_msg.attach_alternative(html_message, "text/html")
        email_msg.send()

        
        return redirect('service_requests:provider_dashboard')

    return render(request, 'service_requests/provider_response_form.html', {'sr': sr, 'existing': existing})



# ---------------------------------------------------------
# 6) RESIDENT SELECTS PROVIDER
# ---------------------------------------------------------
@login_required
def resident_select_provider(request, request_id, response_id):
    sr = get_object_or_404(ServiceRequest, pk=request_id)

    if sr.resident != request.user:
        return HttpResponseForbidden("Not allowed")

    pr = get_object_or_404(ProviderResponse, pk=response_id, service_request=sr)

    ProviderResponse.objects.filter(service_request=sr).update(is_selected_by_resident=False)
    pr.is_selected_by_resident = True
    pr.save()

    sr.confirmed_provider = pr.provider
    sr.set_status(ServiceRequest.STATUS_CONFIRMED)
    sr.save()

    # Notify provider
    subj = f"Your service confirmed — Request #{sr.pk}"
    ctx = {'provider': pr.provider, 'service_request': sr, 'resident': sr.resident}
    html_body = render_to_string('service_requests/emails/provider_selected_by_resident.html', ctx)

    email_msg = EmailMultiAlternatives(
        subject=subj,
        body="Please view this in HTML mode.",
        to=[pr.provider.email]
    )
    email_msg.attach_alternative(html_body, "text/html")
    email_msg.send()

    
    return redirect('service_requests:resident_request_detail', pk=sr.pk)



# ---------------------------------------------------------
# 7) PROVIDER MARKS SERVICE COMPLETED
# ---------------------------------------------------------
@login_required
def provider_mark_completed(request, request_id):
    sr = get_object_or_404(ServiceRequest, pk=request_id)

    try:
        provider = request.user.serviceprovider
    except ServiceProvider.DoesNotExist:
        return HttpResponseForbidden("You are not a provider.")

    if sr.confirmed_provider != provider:
        return HttpResponseForbidden("Only confirmed provider can mark this completed.")

    sr.set_status(ServiceRequest.STATUS_COMPLETED_BY_PROVIDER)

    subj = f"Service marked completed — Request #{sr.pk}"
    ctx = {'service_request': sr, 'provider': provider}
    html_body = render_to_string('service_requests/emails/resident_provider_completed.html', ctx)

    email_msg = EmailMultiAlternatives(
        subject=subj,
        body="Please view this in HTML.",
        to=[sr.email]
    )
    email_msg.attach_alternative(html_body, "text/html")
    email_msg.send()

    
    return redirect('service_requests:provider_dashboard')



# ---------------------------------------------------------
# 8) RESIDENT ACCEPTS COMPLETION
# ---------------------------------------------------------
@login_required
def resident_accept_completion(request, request_id):
    sr = get_object_or_404(ServiceRequest, pk=request_id)

    if sr.resident != request.user:
        return HttpResponseForbidden("Not allowed")

    if request.method == "POST":
        sr.set_status(ServiceRequest.STATUS_COMPLETED_BY_RESIDENT)

        if sr.confirmed_provider:
            provider = sr.confirmed_provider

            subject = f"Service Completed by Resident — Request #{sr.pk}"
            ctx = {
                'service_request': sr,
                'provider': provider,
                'resident': sr.resident,
            }

            html_body = render_to_string(
                'service_requests/emails/provider_services_completed_by_resident.html',
                ctx
            )

            email_msg = EmailMultiAlternatives(
                subject=subject,
                body="Please view this in HTML.",
                to=[provider.email]
            )
            email_msg.attach_alternative(html_body, "text/html")
            email_msg.send()

        
        return redirect('service_requests:submit_feedback', request_id=sr.pk)

    return render(request, 'service_requests/resident_accept_completion.html', {'sr': sr})



# ---------------------------------------------------------
# 9) RESIDENT SUBMITS FEEDBACK
# ---------------------------------------------------------
@login_required
def submit_feedback(request, request_id):
    sr = get_object_or_404(ServiceRequest, pk=request_id)

    if sr.resident != request.user:
        return HttpResponseForbidden("Not allowed")

    if request.method == "POST":
        rating = int(request.POST.get('rating', 0))
        comment = request.POST.get('comment', '')

        if not sr.confirmed_provider:
            return HttpResponseForbidden("Feedback cannot be submitted because no provider was confirmed.")

        feedback, created = ServiceFeedback.objects.get_or_create(
            service_request=sr,
            defaults={
                'provider': sr.confirmed_provider,
                'rating': rating,
                'comment': comment
            }
        )

        if not created:
            feedback.provider = sr.confirmed_provider
            feedback.rating = rating
            feedback.comment = comment
            feedback.save()

        
        return redirect('service_requests:resident_dashboard')

    return render(request, 'service_requests/feedback_form.html', {'sr': sr})
