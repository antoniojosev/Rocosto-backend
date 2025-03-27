from django.contrib import admin

from .models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'tax_id', 'phone', 'user')
    list_filter = ('user',)
    search_fields = ('name', 'tax_id')
    ordering = ('name',)
