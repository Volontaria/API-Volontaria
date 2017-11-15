from django.conf.urls import include, url
from rest_framework.urlpatterns import format_suffix_patterns
from volunteer import views

urlpatterns = format_suffix_patterns(
    [
        # Cycles
        url(
            r'^cycles$',
            views.Cycles.as_view(),
            name='cycles',
        ),
        url(
            r'^cycles/(?P<pk>\d+)$',
            views.CyclesId.as_view(),
            name='cycles_id',
        ),
     ]
)
