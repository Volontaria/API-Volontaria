from rest_framework import generics

from .models import InfoSection
from .serializers import InfoPageSerializer


class InfoPageView(generics.ListAPIView):
    permission_classes = ()
    serializer_class = InfoPageSerializer
    queryset = InfoSection.objects.filter(is_active=True)
