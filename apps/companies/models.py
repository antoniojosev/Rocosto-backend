from django.conf import settings
from django.db import models

from utils.models import BaseModel


class Company(BaseModel):
    """
    Model to manage companies in the system
    """
    tax_id = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Tax ID",
        help_text="Company tax identification number"
    )

    name = models.CharField(
        max_length=255,
        verbose_name="Company Name",
        help_text="Legal name of the company"
    )

    address = models.TextField(
        verbose_name="Address",
        help_text="Complete company address"
    )

    phone = models.CharField(
        max_length=20,
        verbose_name="Phone",
        help_text="Contact phone number"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='companies',
        verbose_name="Owner",
        help_text="User who owns/manages this company"
    )
    owners = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='owner',
        verbose_name="Owners",
        null=True,
    )

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"
        ordering = ['name']
        indexes = [
            models.Index(fields=['tax_id']),
            models.Index(fields=['name'])
        ]

    def __str__(self):
        return f"{self.name} - {self.tax_id}"
