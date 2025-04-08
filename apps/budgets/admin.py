from django.contrib import admin

from .models import Bond, Budget, Retention


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'contract',
                    'budget_date', 'currency')
    search_fields = ('code', 'name', 'contract')
    list_filter = ('currency', 'iva_type', 'use_associated_cost_factor')


@admin.register(Bond)
class BondAdmin(admin.ModelAdmin):
    list_display = ('title', 'budget', 'amount', 'salary_limit_per_day')
    search_fields = ('title', 'budget__name')
    list_filter = ('budget',)


@admin.register(Retention)
class RetentionAdmin(admin.ModelAdmin):
    list_display = ('retention_type', 'budget', 'amount', 'percentage')
    search_fields = ('budget__name',)
    list_filter = ('retention_type', 'budget')
