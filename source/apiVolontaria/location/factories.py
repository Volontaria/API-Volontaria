# coding: utf-8

import factory

from faker import Faker
from .models import *

fake = Faker()


class CountryFactory(factory.DjangoModelFactory):
    class Meta:
        model = Country
        django_get_or_create = ('iso_code',)

    name = fake.country()
    iso_code = fake.country_code()


class StateProvinceFactory(factory.DjangoModelFactory):
    class Meta:
        model = StateProvince

    name = fake.state()
    iso_code = fake.state_abbr()
    country = factory.SubFactory(CountryFactory)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        if 'country' not in kwargs:
            kwargs['country'] = factory.SubFactory(CountryFactory)

        obj = super(StateProvinceFactory, cls)._create(
            model_class, *args, **kwargs)

        return obj


class AddressFactory(factory.DjangoModelFactory):
    class Meta:
        model = Address

    address_line1 = fake.street_address()
    postal_code = fake.postalcode()
    city = fake.city()
    country = factory.SubFactory(CountryFactory)
    state_province = StateProvinceFactory(country=country)
