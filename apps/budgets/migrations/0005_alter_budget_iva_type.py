# Generated by Django 5.1.6 on 2025-03-09 17:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budgets', '0004_budget_state'),
    ]

    operations = [
        migrations.AlterField(
            model_name='budget',
            name='iva_type',
            field=models.CharField(choices=[('NO_IVA', 'No IVA'), ('PRESUPUESTO_VALUACION', 'Budget and Valuation'), (
                'SOLO_VALUACION', 'Valuation Only')], default='PRESUPUESTO_VALUACION', max_length=50),
        ),
    ]
