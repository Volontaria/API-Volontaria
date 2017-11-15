# coding: utf-8

import factory
from django.contrib.auth.models import User


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    username = factory.Sequence('John{0}'.format)
    password = 'Test123!'

    @classmethod
    def _prepare(cls, create, **kwargs):
        if 'password' in kwargs.keys():
            password = kwargs.pop('password', None)

        user = super(UserFactory, cls)._prepare(create, **kwargs)

        if password:
            user.set_password(password)

        user.save()
        return user


class AdminFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    username = factory.Sequence('Chuck{0}'.format)
    password = 'Test123!'
    is_superuser = True

    @classmethod
    def _prepare(cls, create, **kwargs):
        if 'password' in kwargs.keys():
            password = kwargs.pop('password', None)

        user = super(AdminFactory, cls)._prepare(create, **kwargs)

        if password:
            user.set_password(password)

        user.save()
        return user
