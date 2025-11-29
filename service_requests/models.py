from django.conf import settings
from django.db import models
from django.utils import timezone

USER_MODEL = settings.AUTH_USER_MODEL
SERVICE_PROVIDER_MODEL = 'accounts.ServiceProvider'


# ----------------------------------------
# 1) CATEGORY MODEL
# ----------------------------------------
class ServiceCategory(models.Model):
    """Categories like Carpenter, Plumber, Maid, etc."""
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)

    def __str__(self):
        return self.name


# ----------------------------------------
# 2) MAIN SERVICE REQUEST MODEL
# ----------------------------------------
class ServiceRequest(models.Model):

    # Allowed workflow statuses
    STATUS_PENDING = 'pending'
    STATUS_PROVIDER_RESPONSES = 'provider_responses'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_ASSIGNED = 'assigned'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED_BY_PROVIDER = 'completed_by_provider'
    STATUS_COMPLETED_BY_RESIDENT = 'completed_by_resident'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_PROVIDER_RESPONSES, 'Waiting Provider Responses'),
        (STATUS_CONFIRMED, 'Confirmed by Resident'),
        (STATUS_ASSIGNED, 'Assigned'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_COMPLETED_BY_PROVIDER, 'Completed by Provider'),
        (STATUS_COMPLETED_BY_RESIDENT, 'Completed by Resident'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    # Link Resident User
    resident = models.ForeignKey(
        USER_MODEL,
        on_delete=models.CASCADE,
        related_name='service_requests'
    )

    # Category—Plumber, Carpenter etc.
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.PROTECT,
        related_name='requests'
    )

    # Snapshot resident details
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=30)
    email = models.EmailField()
    apartment_details = models.TextField()

    preferred_date = models.DateField(null=True, blank=True)
    preferred_time = models.TimeField(null=True, blank=True)
    details = models.TextField(blank=True)

    # If provider proposes new time
    provider_proposed_date = models.DateField(null=True, blank=True)
    provider_proposed_time = models.TimeField(null=True, blank=True)

    has_provider_responses = models.BooleanField(default=False)

    # Rating moved to feedback model
    # feedback moved to feedback model

    status = models.CharField(
        max_length=40,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    confirmed_provider = models.ForeignKey(
        SERVICE_PROVIDER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='confirmed_requests'
    )

    def __str__(self):
        return f"Request #{self.pk} — {self.category.name} — {self.resident}"

    def set_status(self, status):
        self.status = status
        self.updated_at = timezone.now()
        self.save(update_fields=['status', 'updated_at'])


# ----------------------------------------
# 3) PROVIDER RESPONSE MODEL
# ----------------------------------------
class ProviderResponse(models.Model):
    """Each provider can respond only once to each service request."""

    ACTION_ACCEPT = 'accept'
    ACTION_REJECT = 'reject'
    ACTION_PROPOSE = 'propose'

    ACTION_CHOICES = [
        (ACTION_ACCEPT, 'Accept'),
        (ACTION_REJECT, 'Reject'),
        (ACTION_PROPOSE, 'Propose New Time'),
    ]

    service_request = models.ForeignKey(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name='provider_responses'
    )

    provider = models.ForeignKey(
        SERVICE_PROVIDER_MODEL,
        on_delete=models.CASCADE,
        related_name='responses'
    )

    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    message = models.TextField(blank=True, null=True)

    proposed_date = models.DateField(blank=True, null=True)
    proposed_time = models.TimeField(blank=True, null=True)

    created_at = models.DateTimeField(default=timezone.now)

    # When resident chooses the final provider
    is_selected_by_resident = models.BooleanField(default=False)

    class Meta:
        unique_together = ('service_request', 'provider')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.provider} → Request #{self.service_request.id} ({self.action})"


# ----------------------------------------
# 4) FEEDBACK MODEL
# ----------------------------------------
class ServiceFeedback(models.Model):
    service_request = models.OneToOneField(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name='feedback'
    )

    provider = models.ForeignKey(
        SERVICE_PROVIDER_MODEL,
        on_delete=models.CASCADE,
        related_name='feedbacks'
    )

    rating = models.PositiveSmallIntegerField()  # 1–5 stars
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback {self.rating}★ for Request #{self.service_request.pk}"  

