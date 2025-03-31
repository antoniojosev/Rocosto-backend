from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.databases.views.views import (
    DatabaseResourceStatsViewSet,
    EquipmentViewSet,
    LaborViewSet,
    MaterialViewSet,
    UnitViewSet,
    WorkItemViewSet,
)

router = DefaultRouter()
router.register(r'units', UnitViewSet)
router.register(r'materials', MaterialViewSet)
router.register(r'equipment', EquipmentViewSet)
router.register(r'labor', LaborViewSet)
router.register(r'work-items', WorkItemViewSet)
router.register(r'', DatabaseResourceStatsViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
