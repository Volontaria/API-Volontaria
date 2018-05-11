
from rest_framework import generics, status

from . import models, serializers


class Faq(generics.ListAPIView):
    serializer_class = serializers.FaqSerializer

    def get_queryset(self):
        return models.Faq.objects.filter(is_active=True)


class FaqCategoryId(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = serializers.FaqCategorySerializer

    def get_queryset(self):
       return models.FaqCategory.objects.filter(is_active=True)


class FaqCategory(generics.ListAPIView):
    serializer_class = serializers.FaqCategorySerializer

    def get_queryset(self):
        return models.FaqCategory.objects.filter(is_active=True)
