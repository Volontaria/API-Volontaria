import stripe
from requests import Response
from rest_framework import status, generics, viewsets
from rest_framework.decorators import api_view, action

from api_volontaria.apps.donation.models import Donation
from api_volontaria.apps.donation.serializers import DonationSerializer


class DonationViewSet(viewsets.ModelViewSet):
    serializer_class = DonationSerializer
    queryset = Donation.objects.all()
