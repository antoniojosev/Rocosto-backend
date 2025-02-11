# Register your models here.
from django.contrib import admin

from .models import Database, Equipment, Labor, Material, Unit, WorkItem

admin.site.register(Unit)
admin.site.register(Database)
admin.site.register(Material)
admin.site.register(Equipment)
admin.site.register(Labor)
admin.site.register(WorkItem)
