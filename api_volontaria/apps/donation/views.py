from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from dry_rest_permissions.generics import DRYPermissions, \
    DRYPermissionFiltersBase
from rest_framework import viewsets

from api_volontaria.apps.donation.models import (
    BankConnection,
    StripeConnection,
    Donation,
)
from api_volontaria.apps.donation.serializers import (
    BankConnectionSerializer,
    StripeConnectionSerializer,
    DonationSerializer,
)
# Create your views here.

class BankConnectionViewSet(viewsets.ModelViewSet):

    queryset = BankConnection.objects.all()
    serializer_class = BankConnectionSerializer
    filter_fields = '__all__'
    permission_classes = (DRYPermissions,)
    
class StripeConnectionViewSet(viewsets.ModelViewSet):

    queryset = StripeConnection.objects.all()
    serializer_class = StripeConnectionSerializer
    filter_fields = '__all__'
    permission_classes = (DRYPermissions,)
    
class DonationViewSet(viewsets.ModelViewSet):

    queryset = Donation.objects.all()
    serializer_class = DonationSerializer
    filter_fields = '__all__'
    permission_classes = (DRYPermissions,)