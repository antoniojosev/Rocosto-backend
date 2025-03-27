from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from apps.companies.models import Company
from apps.databases.models import WorkItem
from apps.users.models import User
from utils.models import BaseModel


class Budget(BaseModel):
    """
    Budget model for managing project and construction budgets.
    """
    class IVAChoices(models.TextChoices):
        NO_IVA = 'NO_IVA', 'No IVA'
        PRESUPUESTO_VALUACION = 'PRESUPUESTO_VALUACION', 'Budget and Valuation'
        SOLO_VALUACION = 'SOLO_VALUACION', 'Valuation Only'

    class CurrencyChoices(models.TextChoices):
        BS = 'BS', 'Bolivares'
        USD = 'USD', 'Dollars'
        SOL = 'SOL', 'Solana'

    class StateChoices(models.TextChoices):
        IN_PROGRESS = 'IN_PROGRESS', 'In Progress'
        PENDING = 'PENDING', 'Pending'
        FINISHED = 'FINISHED', 'Finished'

    state = models.CharField(
        max_length=20,
        choices=StateChoices.choices,
        default=StateChoices.IN_PROGRESS
    )

    # General Data
    code = models.CharField(
        max_length=50,
        unique=True
    )
    contract = models.CharField(
        max_length=100
    )
    budget_date = models.DateField()
    name = models.CharField(
        max_length=255
    )
    owner = models.CharField(
        max_length=255
    )
    calculated_by = models.CharField(
        max_length=100
    )
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_budgets'
    )
    hours_per_day = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=8.00,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    currency = models.CharField(
        max_length=3,
        choices=CurrencyChoices.choices,
        default=CurrencyChoices.USD
    )

    # Salary Associated Costs
    use_associated_cost_factor = models.BooleanField(
        default=False
    )
    direct_labor_factor = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=1005.00,
        validators=[MinValueValidator(Decimal('0.01'))]
    )

    # Taxes
    iva_type = models.CharField(
        max_length=50,
        choices=IVAChoices.choices,
        default=IVAChoices.PRESUPUESTO_VALUACION
    )
    iva_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=12.00,
        validators=[MinValueValidator(Decimal('0.00'))]
    )

    # Indirect Cost Factors
    administration_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=16.00,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    utility_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=15.00,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    financing_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(Decimal('0.00'))]
    )

    # Other Factors
    use_medical_insurance = models.BooleanField(
        default=False
    )

    # User Relationship
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='budgets'
    )
    work_item = models.ManyToManyField(WorkItem)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} - {self.name}"


class Bond(BaseModel):
    """
    Model for managing bonds associated with a budget.
    """
    budget = models.ForeignKey(
        Budget,
        on_delete=models.CASCADE,
        related_name='bonds'
    )
    title = models.CharField(
        max_length=100
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00
    )
    salary_limit_per_day = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00
    )

    class Meta:
        ordering = ['title']

    def __str__(self):
        return f"{self.title} - {self.amount}"


class Retention(BaseModel):
    """
    Model for managing retentions or advances associated with a budget.
    """
    class RetentionType(models.TextChoices):
        ADVANCE = 'ADVANCE', 'Advance'
        LABOR = 'LABOR', 'Labor Retention'
        COMPLIANCE = 'COMPLIANCE', 'Compliance Retention'

    budget = models.ForeignKey(
        Budget,
        on_delete=models.CASCADE,
        related_name='retentions'
    )
    retention_type = models.CharField(
        max_length=20,
        choices=RetentionType.choices
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00
    )
    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(Decimal('0.00'))]
    )

    class Meta:
        ordering = ['retention_type']

    def __str__(self):
        return f"{self.retention_type} - {self.percentage}%"
