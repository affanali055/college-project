from django.db import models
from django.conf import settings
from workspaces.models import WorkspaceUnit, CoWorkingSpace

class PromoCode(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount_percent = models.PositiveIntegerField(help_text="Discount percentage, e.g. 10 for 10% off")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} ({self.discount_percent}% off)"

class Booking(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('CANCELLED', 'Cancelled'),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    unit = models.ForeignKey(
        WorkspaceUnit,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    start_date = models.DateField()
    end_date = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    promo_code = models.ForeignKey(PromoCode, on_delete=models.SET_NULL, blank=True, null=True, related_name='bookings')
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def duration_days(self):
        delta = self.end_date - self.start_date
        return max(1, delta.days + 1)

    def calculate_total_price(self):
        return self.unit.price_per_day * self.duration_days()

    def __str__(self):
        return f"{self.user.username} - {self.unit.name} ({self.start_date} to {self.end_date})"

class Inquiry(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_inquiries'
    )
    space = models.ForeignKey(
        CoWorkingSpace,
        on_delete=models.CASCADE,
        related_name='inquiries'
    )
    message = models.TextField()
    expectations = models.TextField(
        blank=True,
        null=True,
        help_text="Provide details about your team workstyle and expectations for mutual matching"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='replies'
    )

    class Meta:
        verbose_name_plural = "Inquiries"
        ordering = ['created_at']

    def __str__(self):
        return f"Inquiry by {self.sender.username} regarding {self.space.name}"
