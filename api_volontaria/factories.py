import factory
from django.contrib.auth import get_user_model

User = get_user_model()


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Sequence('john{0}@example.com'.format)
    password = 'Test123!'


class AdminFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Sequence('chuck{0}@example.com'.format)
    password = 'Test123!'
    is_staff = True
