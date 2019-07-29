from django.conf.urls import include, url
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

app_name = 'location'

urlpatterns = format_suffix_patterns(
    [
        # Addresses
        url(
            r'^addresses$',
            views.Addresses.as_view(),
            name='addresses',
        ),
        url(
            r'^addresses/(?P<pk>\d+)$',
            views.AddressesId.as_view(),
            name='addresses_id',
        ),
        # StateProvince
        url(
            r'^stateprovinces$',
            views.StateProvinces.as_view(),
            name='stateprovinces',
        ),
        url(
            r'^stateprovinces/(?P<pk>[a-zA-Z]+)$',
            views.StateProvincesId.as_view(),
            name='stateprovinces_id',
        ),
        # Country
        url(
            r'^countries$',
            views.Countries.as_view(),
            name='countries',
        ),
        url(
            r'^countries/(?P<pk>[a-zA-Z]+)$',
            views.CountriesId.as_view(),
            name='countries_id',
        ),
    ]
)
