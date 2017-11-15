from rest_framework import generics, filters
from volunteer import models, serializers
from rest_framework import status
from rest_framework.response import Response


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
                'detail': "You're not authorized to create a new cycle.",
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
                'detail': "You're not authorized to update a cycle.",
            }
            return Response(content, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, *args, **kwargs):
        if self.request.user.has_perm('volunteer.delete_cycle'):
            return self.destroy(request, *args, **kwargs)
        else:
            content = {
                'detail': "You're not authorized to delete a cycle.",
            }
            return Response(content, status=status.HTTP_403_FORBIDDEN)
