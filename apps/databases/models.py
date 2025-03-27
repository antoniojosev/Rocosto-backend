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
        on_delete=models.SET_NULL,
        related_name='databases',
        blank=True,
        null=True
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
        on_delete=models.SET_NULL,
        related_name='materials',
        blank=True,
        null=True
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
    material = models.ManyToManyField(Material)
    labor = models.ManyToManyField(Labor)
    equipment = models.ManyToManyField(Equipment)
    database = models.ForeignKey(
        Database,
        on_delete=models.CASCADE,
        related_name='work_items'
    )
    covening_code = models.CharField(max_length=50, blank=True, null=True)
    MATERIAL_USAGE_CALCULATION_CHOICES = [
        ('UNITARY', 'Unitario'),
        ('DIVIDED', 'Dividido por la cantidad'),
    ]
    material_unit_usage = models.CharField(
        max_length=10,
        choices=MATERIAL_USAGE_CALCULATION_CHOICES,
        default='UNITARY'
    )

    def __str__(self):
        return f"{self.code} - {self.description}"

    def get_total_labor_cost(self):
        """Calculate the sum of hourly costs for all labor in this work item"""
        return self.labor.aggregate(total=models.Sum('hourly_cost'))['total'] or 0

    def get_total_equipment_cost(self):
        """Calculate the sum of costs for all equipment in this work item"""
        return self.equipment.aggregate(total=models.Sum('cost'))['total'] or 0

    def get_total_material_cost(self):
        """Calculate the sum of costs for all materials in this work item"""
        return self.material.aggregate(total=models.Sum('cost'))['total'] or 0

    def get_total_cost(self):
        """Calculate the total cost by summing labor, equipment and material costs"""
        return (self.get_total_labor_cost() +
                self.get_total_equipment_cost() +
                self.get_total_material_cost())

    class Meta:
        verbose_name = "Work Item"
        verbose_name_plural = "Work Items"
        unique_together = ['code', 'database']
