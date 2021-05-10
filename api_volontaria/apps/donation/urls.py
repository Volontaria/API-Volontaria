# from api_volontaria.apps.donation.views import DonationViewSet
#
# snippet_list = DonationViewSet.as_view({
#     'get': 'list',
#     'post': 'create'
# })


from rest_framework.routers import SimpleRouter
from django.urls import path
from django.conf.urls import include

from . import views


class OptionalSlashSimpleRouter(SimpleRouter):
    """ Subclass of SimpleRouter to make the trailing slash optional """

    def __init__(self, *args, **kwargs):
        super(SimpleRouter, self).__init__(*args, **kwargs)
        self.trailing_slash = '/?'


app_name = "donation"

router = OptionalSlashSimpleRouter()
router.register('donations', views.DonationViewSet)

urlpatterns = [
    path('', include(router.urls)),  # includes router generated URL
]
