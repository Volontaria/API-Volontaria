from rest_framework.routers import SimpleRouter
from django.urls import path
from django.conf.urls import include

from . import views


class OptionalSlashSimpleRouter(SimpleRouter):
    """ Subclass of SimpleRouter to make the trailing slash optional """

    def __init__(self, *args, **kwargs):
        super(SimpleRouter, self).__init__(*args, **kwargs)
        self.trailing_slash = '/?'


app_name = "volunteer"

# Create a router and register our viewsets with it.
router = OptionalSlashSimpleRouter()
router.register('cells', views.CellViewSet)
router.register('task_types', views.TaskTypeViewSet)
router.register('events', views.EventViewSet)
router.register('participations', views.ParticipationViewSet)

urlpatterns = [
    path('', include(router.urls)),  # includes router generated URL
]
