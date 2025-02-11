# Create your models here.
from django.conf import settings
from django.db import models

from utils.models import BaseModel


class Unit(BaseModel):
    """Model for units of measurement"""
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.name} ({self.symbol})"

    class Meta:
        verbose_name = "Unit"
        verbose_name_plural = "Units"


class Database(BaseModel):
    """Model for construction databases"""
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='databases'
    )

    def __str__(self):
        return f"{self.code} - {self.name}"

    class Meta:
        verbose_name = "Database"
        verbose_name_plural = "Databases"
        ordering = ['code']


class Material(BaseModel):
    """Model for construction materials"""
    code = models.CharField(max_length=50)
    description = models.TextField()
    unit = models.ForeignKey(
        Unit,
        on_delete=models.CASCADE,
        related_name='unit_material'
    )
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    database = models.ForeignKey(
        Database,
        on_delete=models.CASCADE,
        related_name='materials'
    )

    def __str__(self):
        return f"{self.code} - {self.description}"

    class Meta:
        verbose_name = "Material"
        verbose_name_plural = "Materials"
        unique_together = ['code', 'database']


class Equipment(BaseModel):
    """Model for construction equipment"""
    code = models.CharField(max_length=50)
    description = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    depreciation = models.DecimalField(max_digits=5, decimal_places=2)
    database = models.ForeignKey(
        Database,
        on_delete=models.CASCADE,
        related_name='equipment'
    )

    def __str__(self):
        return f"{self.code} - {self.description}"

    class Meta:
        verbose_name = "Equipment"
        verbose_name_plural = "Equipment"
        unique_together = ['code', 'database']


class Labor(BaseModel):
    """Model for labor resources"""
    code = models.CharField(max_length=50)
    description = models.TextField()
    hourly_cost = models.DecimalField(max_digits=10, decimal_places=2)
    database = models.ForeignKey(
        Database,
        on_delete=models.CASCADE,
        related_name='labor'
    )

    def __str__(self):
        return f"{self.code} - {self.description}"

    class Meta:
        verbose_name = "Labor"
        verbose_name_plural = "Labor"
        unique_together = ['code', 'database']


class WorkItem(BaseModel):
    """Model for construction work items"""
    code = models.CharField(max_length=50)
    description = models.TextField()
    unit = models.CharField(max_length=50)
    yield_rate = models.DecimalField(max_digits=10, decimal_places=2)
    materials = models.ManyToManyField(Material)
    labor = models.ManyToManyField(Labor)
    equipment = models.ManyToManyField(Equipment)
    database = models.ForeignKey(
        Database,
        on_delete=models.CASCADE,
        related_name='work_items'
    )

    def __str__(self):
        return f"{self.code} - {self.description}"

    class Meta:
        verbose_name = "Work Item"
        verbose_name_plural = "Work Items"
        unique_together = ['code', 'database']
