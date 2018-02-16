# coding: utf-8

import factory
import factory.fuzzy

from .models import *
from location.factories import AddressFactory
from apiVolontaria.factories import UserFactory
from faker import Faker

fake = Faker()


class CellFactory(factory.DjangoModelFactory):
    class Meta:
        model = Cell

    name = fake.lexify(text="????????")
    address = factory.SubFactory(AddressFactory)


class CycleFactory(factory.DjangoModelFactory):
    class Meta:
        model = Cycle

    name = fake.lexify(text="????????")


class TaskTypeFactory(factory.DjangoModelFactory):
    class Meta:
        model = TaskType

    name = fake.lexify(text="????????")


class EventFactory(factory.DjangoModelFactory):

    start_date = factory.LazyFunction(timezone.now)
    end_date = factory.LazyFunction(timezone.now)
    cell = factory.SubFactory(CellFactory)
    cycle = factory.SubFactory(CycleFactory)
    task_type = factory.SubFactory(TaskTypeFactory)

    class Meta:
        model = Event

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        if 'end_date' in kwargs.keys():
            now = timezone.now()
            kwargs['end_date'] = now + timezone.timedelta(minutes=100)

        event = super(EventFactory, cls)._create(model_class, *args, **kwargs)

        return event


class ParticipationFactory(factory.DjangoModelFactory):

    class Meta:
        model = Participation

    event = factory.SubFactory(EventFactory)
    user = factory.SubFactory(UserFactory)
    standby = True
    subscription_date = factory.LazyFunction(timezone.now)
