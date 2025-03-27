from rest_framework.routers import DefaultRouter

from apps.budgets.views.views import BudgetViewSet

router = DefaultRouter()
router.register(r'budgets', BudgetViewSet, basename='budget')

urlpatterns = router.urls
