from rest_framework import generics

from pages.models import InfoSection
from pages.serializers import InfoPageSerializer


class InfoPageView(generics.ListAPIView):
    permission_classes = ()
    serializer_class = InfoPageSerializer
    queryset = InfoSection.objects.filter(is_active=True)
