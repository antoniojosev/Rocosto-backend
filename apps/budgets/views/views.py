from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.budgets.models import Budget
from apps.budgets.serializers.serializers import (
    BudgetCreateSerializer,
    BudgetSerializer,
    BudgetUpdateSerializer,
)


class BudgetViewSet(viewsets.ModelViewSet):
    """
    ViewSet for viewing and editing budgets.
    """
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return BudgetCreateSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return BudgetUpdateSerializer
        return self.serializer_class

    def get_queryset(self):
        """
        This view should return a list of all budgets
        for the currently authenticated user.
        """
        return Budget.objects.filter(user=self.request.user)
