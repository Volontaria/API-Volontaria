from rest_framework import generics, filters
from rest_framework import status
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
