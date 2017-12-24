from rest_framework import generics, filters, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from . import models, serializers


class Cycles(generics.ListCreateAPIView):
    """
    get:
    Return a list of all the existing cycles.

    post:
    Create a new cycles.
    """
    serializer_class = serializers.CycleBasicSerializer

    def get_queryset(self):
        return models.Cycle.objects.filter()

    def post(self, request, *args, **kwargs):
        if self.request.user.has_perm('volunteer.add_cycle'):
            return self.create(request, *args, **kwargs)
        else:
            content = {
                'detail': "You are not authorized to create a new cycle.",
            }
            return Response(content, status=status.HTTP_403_FORBIDDEN)


class CyclesId(generics.RetrieveUpdateDestroyAPIView):
    """
    get:
    Return the detail of a specific cycle.

    patch:
    Update a specific cycle.

    delete:
    Delete a specific cycle.
    """
    serializer_class = serializers.CycleBasicSerializer

    def get_queryset(self):
        return models.Cycle.objects.filter()

    def patch(self, request, *args, **kwargs):
        if self.request.user.has_perm('volunteer.update_cycle'):
            return self.update(request, *args, **kwargs)
        else:
            content = {
                'detail': "You are not authorized to update a cycle.",
            }
            return Response(content, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, *args, **kwargs):
        if self.request.user.has_perm('volunteer.delete_cycle'):
            return self.destroy(request, *args, **kwargs)
        else:
            content = {
                'detail': "You are not authorized to delete a cycle.",
            }
            return Response(content, status=status.HTTP_403_FORBIDDEN)


class TaskTypes(generics.ListCreateAPIView):

    """

    get:
    Return a list of all the existing TaskTypes.

    post:
    Create a new TaskType.

    """

    serializer_class = serializers.TaskTypeBasicSerializer

    def get_queryset(self):
        return models.TaskType.objects.filter()

    def post(self, request, *args, **kwargs):
        if self.request.user.has_perm('volunteer.add_tasktype'):
            return self.create(request, *args, **kwargs)

        content = {
            'detail': "You are not authorized to create a new tasktype.",
        }
        return Response(content, status=status.HTTP_403_FORBIDDEN)


class TaskTypesId(generics.RetrieveUpdateDestroyAPIView):

    """

    This class holds the methods available to individual TaskTypes.

    get:
    Return the detail of a specific TaskType.

    patch:
    Update a specific TaskType.

    delete:
    Delete a specific TaskType.

    """

    serializer_class = serializers.TaskTypeBasicSerializer

    def get_queryset(self):
        return models.TaskType.objects.filter()

    def patch(self, request, *args, **kwargs):
        if self.request.user.has_perm('volunteer.update_tasktype'):
            return self.update(request, *args, **kwargs)

        content = {
            'detail': "You are not authorized to update a tasktype.",
        }
        return Response(content, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, *args, **kwargs):
        if self.request.user.has_perm('volunteer.delete_tasktype'):
            return self.destroy(request, *args, **kwargs)

        content = {
            'detail': "You are not authorized to delete a tasktype.",
        }
        return Response(content, status=status.HTTP_403_FORBIDDEN)


class Cells(generics.ListCreateAPIView):

    """

    get:
    Return a list of all the existing Cells.

    post:
    Create a new Cell.

    """

    serializer_class = serializers.CellBasicSerializer

    def get_queryset(self):
        return models.Cell.objects.filter()

    def post(self, request, *args, **kwargs):
        if self.request.user.has_perm('volunteer.add_cell'):
            return self.create(request, *args, **kwargs)

        content = {
            'detail': "You are not authorized to create a new cell.",
        }
        return Response(content, status=status.HTTP_403_FORBIDDEN)


class CellsId(generics.RetrieveUpdateDestroyAPIView):

    """

    This class holds the methods available to individual Cells.

    get:
    Return the detail of a specific Cell.

    patch:
    Update a specific Cell.

    delete:
    Delete a specific Cell.

    """

    serializer_class = serializers.CellBasicSerializer

    def get_queryset(self):
        return models.Cell.objects.filter()

    def patch(self, request, *args, **kwargs):
        if self.request.user.has_perm('volunteer.update_cell'):
            return self.update(request, *args, **kwargs)

        content = {
            'detail': "You are not authorized to update a cell.",
        }
        return Response(content, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, *args, **kwargs):
        if self.request.user.has_perm('volunteer.delete_cell'):
            return self.destroy(request, *args, **kwargs)

        content = {
            'detail': "You are not authorized to delete a cell.",
        }
        return Response(content, status=status.HTTP_403_FORBIDDEN)


class Events(generics.ListCreateAPIView):

    """

    get:
    Return a list of all the existing Events.

    post:
    Create a new Event.

    """

    serializer_class = serializers.EventBasicSerializer

    def get_queryset(self):
        if self.request.user.has_perm('volunteer.add_event'):
            return models.Event.objects.all()
        else:
            queryset = models.Event.objects.all()

            list_exclude = list()
            for event in queryset:
                if not event.is_active:
                    list_exclude.append(event)

            queryset = queryset.\
                exclude(pk__in=[event.pk for event in list_exclude])

            return queryset

    def post(self, request, *args, **kwargs):
        if self.request.user.has_perm('volunteer.add_event'):
            return self.create(request, *args, **kwargs)

        content = {
            'detail': "You are not authorized to create a new event.",
        }
        return Response(content, status=status.HTTP_403_FORBIDDEN)


class EventsId(generics.RetrieveUpdateDestroyAPIView):

    """

    This class holds the methods available to individual Events.

    get:
    Return the detail of a specific Event.

    patch:
    Update a specific Event.

    delete:
    Delete a specific Event.

    """

    serializer_class = serializers.EventBasicSerializer

    def get_queryset(self):
        return models.Event.objects.filter()

    def patch(self, request, *args, **kwargs):
        if self.request.user.has_perm('volunteer.update_event'):
            return self.partial_update(request, *args, **kwargs)

        content = {
            'detail': "You are not authorized to update an event.",
        }
        return Response(content, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, *args, **kwargs):
        if self.request.user.has_perm('volunteer.delete_event'):
            return self.destroy(request, *args, **kwargs)

        content = {
            'detail': "You are not authorized to delete an event.",
        }
        return Response(content, status=status.HTTP_403_FORBIDDEN)
