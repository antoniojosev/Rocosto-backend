# Generated by Django 5.1.6 on 2025-03-08 21:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budgets', '0001_initial'),
        ('databases', '0002_database_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='budget',
            name='work_item',
            field=models.ManyToManyField(to='databases.workitem'),
        ),
    ]
