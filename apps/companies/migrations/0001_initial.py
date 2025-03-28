# Generated by Django 5.1.6 on 2025-02-11 23:39

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4,
                 editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('tax_id', models.CharField(help_text='Company tax identification number',
                 max_length=20, unique=True, verbose_name='Tax ID')),
                ('name', models.CharField(help_text='Legal name of the company',
                 max_length=255, verbose_name='Company Name')),
                ('address', models.TextField(
                    help_text='Complete company address', verbose_name='Address')),
                ('phone', models.CharField(help_text='Contact phone number',
                 max_length=20, verbose_name='Phone')),
                ('user', models.ForeignKey(help_text='User who owns/manages this company', on_delete=django.db.models.deletion.CASCADE,
                 related_name='companies', to=settings.AUTH_USER_MODEL, verbose_name='Owner')),
            ],
            options={
                'verbose_name': 'Company',
                'verbose_name_plural': 'Companies',
                'ordering': ['name'],
                'indexes': [models.Index(fields=['tax_id'], name='companies_c_tax_id_b95ae4_idx'), models.Index(fields=['name'], name='companies_c_name_2d8260_idx')],
            },
        ),
    ]
