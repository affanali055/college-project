from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('CLIENT', 'Client / Freelancer'),
        ('OWNER', 'Space Owner'),
        ('ADMIN', 'Administrator'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='CLIENT')
    phone = models.CharField(max_length=15, blank=True, null=True)
    company_name = models.CharField(max_length=100, blank=True, null=True)

    def is_client(self):
        return self.role == 'CLIENT'

    def is_owner(self):
        return self.role == 'OWNER'

    def is_administrator(self):
        return self.role == 'ADMIN' or self.is_superuser

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
