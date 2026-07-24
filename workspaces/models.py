from django.db import models
from django.conf import settings

class Amenity(models.Model):
    name = models.CharField(max_length=50, unique=True)
    icon_class = models.CharField(max_length=50, blank=True, help_text="Standard icon name, e.g., wifi, parking, coffee")

    class Meta:
        verbose_name_plural = "Amenities"

    def __str__(self):
        return self.name

class CoWorkingSpace(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='spaces'
    )
    name = models.CharField(max_length=100)
    description = models.TextField()
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    amenities = models.ManyToManyField(Amenity, blank=True, related_name='spaces')
    image_url = models.URLField(max_length=500, blank=True, null=True, help_text="URL of space thumbnail image")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_min_price(self):
        units = self.units.all()
        if not units:
            return 0
        prices = [u.price_per_day for u in units if u.price_per_day > 0]
        return min(prices) if prices else 0

    def get_max_capacity(self):
        units = self.units.all()
        return max([u.seating_capacity for u in units]) if units else 0

    def __str__(self):
        return f"{self.name} - {self.city}"

class WorkspaceUnit(models.Model):
    UNIT_TYPES = (
        ('CABIN', 'Private Cabin'),
        ('DESK', 'Shared Desk'),
        ('MEETING', 'Meeting Room'),
    )
    space = models.ForeignKey(
        CoWorkingSpace,
        on_delete=models.CASCADE,
        related_name='units'
    )
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=UNIT_TYPES, default='DESK')
    seating_capacity = models.PositiveIntegerField(help_text="Number of persons this unit accommodates")
    area_sqft = models.DecimalField(max_digits=8, decimal_places=2, help_text="Area in square feet")
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.space.name} - {self.name} ({self.get_type_display()})"
