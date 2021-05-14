import factory
from django.contrib.auth import get_user_model

User = get_user_model()


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User
    # Using fixed first name and last name
    # instead of factory.Faker('first_name') and factory.F('last_name')
    # respectively, so that test_password_change_but_too_weak
    # in test_view_users.py
    # always returns the same message
    # (with a random first name and last name, risk that
    # 'test' password is too similar to first name or last name,
    # which randomly triggers a different message than 
    # the message expected in the test)
    first_name = 'Charles'
    last_name = 'Baudelaire'
    email = factory.Sequence('john{0}@example.com'.format)
    password = 'Test123!'


class AdminFactory(factory.DjangoModelFactory):
    class Meta:
        model = User
    first_name = 'Victor'
    last_name = 'Hugo'
    email = factory.Sequence('chuck{0}@example.com'.format)
    password = 'Test123!'
    is_staff = True
