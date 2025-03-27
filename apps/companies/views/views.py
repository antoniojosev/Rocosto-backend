from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.companies.models import Company
from apps.companies.serializers.serializers import CompanySerializer


class CompanyViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing Company instances"""
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset to return only user's companies"""
        return Company.objects.filter(user=self.request.user)
