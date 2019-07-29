from rest_framework.response import Response
from rest_framework import status, generics

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from . import serializers

from .models import Address, Country, StateProvince


class Addresses(generics.ListCreateAPIView):
    """
    get:
    Return a list of all the existing Addresses.

    post:
    Create a new Address.
    """
    serializer_class = serializers.AddressBasicSerializer

    def get_queryset(self):
        return Address.objects.filter()

    def post(self, request, *args, **kwargs):
        if self.request.user.has_perm('add_address'):
            try:
                return self.create(request, *args, **kwargs)
            except ValidationError as err:
                content = dict(detail=err.message)
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

        content = {
            'detail': _("You are not authorized to create a new address."),
        }
        return Response(content, status=status.HTTP_403_FORBIDDEN)


class AddressesId(generics.RetrieveUpdateDestroyAPIView):
    """
    get:
    Return the detail of a specific Address.

    patch:
    Update a specific Address.

    delete:
    Delete a specific Address.
    """
    serializer_class = serializers.AddressBasicSerializer

    def get_queryset(self):
        return Address.objects.filter()

    def patch(self, request, *args, **kwargs):
        if self.request.user.has_perm('change_address'):
            try:
                return self.partial_update(request, *args, **kwargs)
            except ValidationError as err:
                content = dict(detail=err.message)
                return Response(content, status=status.HTTP_400_BAD_REQUEST)

        content = {
            'detail': _("You are not authorized to update an address."),
        }
        return Response(content, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, *args, **kwargs):
        if self.request.user.has_perm('delete_address'):
            return self.destroy(request, *args, **kwargs)

        content = {
            'detail': _("You are not authorized to delete an address."),
        }
        return Response(content, status=status.HTTP_403_FORBIDDEN)


class Countries(generics.ListCreateAPIView):
    """
    get:
    Return a list of all the existing Countries.

    post:
    Create a new Country.
    """
    serializer_class = serializers.CountryBasicSerializer

    def get_queryset(self):
        return Country.objects.all()

    def post(self, request, *args, **kwargs):
        if self.request.user.has_perm('add_country'):
            return self.create(request, *args, **kwargs)

        content = {
            'detail': _("You are not authorized to create a new country."),
        }
        return Response(content, status=status.HTTP_403_FORBIDDEN)


class CountriesId(generics.RetrieveUpdateDestroyAPIView):
    """
    get:
    Return the detail of a specific Country.

    patch:
    Update a specific Country.

    delete:
    Delete a specific Country.
    """
    serializer_class = serializers.CountryBasicSerializer

    def get_queryset(self):
        return Country.objects.filter()

    def patch(self, request, *args, **kwargs):
        if self.request.user.has_perm('change_country'):
            return self.partial_update(request, *args, **kwargs)

        content = {
            'detail': _("You are not authorized to update a country."),
        }
        return Response(content, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, *args, **kwargs):
        if self.request.user.has_perm('delete_country'):
            return self.destroy(request, *args, **kwargs)

        content = {
            'detail': _("You are not authorized to delete a country."),
        }
        return Response(content, status=status.HTTP_403_FORBIDDEN)


class StateProvinces(generics.ListCreateAPIView):
    """
    get:
    Return a list of all the existing StateProvince.

    post:
    Create a new StateProvince.
    """
    serializer_class = serializers.StateProvinceBasicSerializer

    def get_queryset(self):
        return StateProvince.objects.filter()

    def post(self, request, *args, **kwargs):
        if self.request.user.has_perm('add_stateprovince'):
            return self.create(request, *args, **kwargs)

        content = {
            'detail': _("You are not authorized to create a "
                        "new stateprovince."),
        }
        return Response(content, status=status.HTTP_403_FORBIDDEN)


class StateProvincesId(generics.RetrieveUpdateDestroyAPIView):
    """
    get:
    Return the detail of a specific StateProvince.

    patch:
    Update a specific StateProvince.

    delete:
    Delete a specific StateProvince.
    """
    serializer_class = serializers.StateProvinceBasicSerializer

    def get_queryset(self):
        return StateProvince.objects.filter()

    def patch(self, request, *args, **kwargs):
        if self.request.user.has_perm('change_stateprovince'):
            return self.partial_update(request, *args, **kwargs)

        content = {
            'detail': _("You are not authorized to update a stateprovince."),
        }
        return Response(content, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, *args, **kwargs):
        if self.request.user.has_perm('delete_stateprovince'):
            return self.destroy(request, *args, **kwargs)

        content = {
            'detail': _("You are not authorized to delete a stateprovince."),
        }
        return Response(content, status=status.HTTP_403_FORBIDDEN)
