from django.conf.urls import include, url
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

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
        # Tasktypes
        url(
            r'^tasktypes$',
            views.TaskTypes.as_view(),
            name='tasktypes',
        ),
        url(
            r'^tasktypes/(?P<pk>\d+)$',
            views.TaskTypesId.as_view(),
            name='tasktypes_id',
        ),
        # Cells
        url(
            r'^cells$',
            views.Cells.as_view(),
            name='cells',
        ),
        url(
            r'^cells/(?P<pk>\d+)$',
            views.CellsId.as_view(),
            name='cells_id',
        ),
    ]
)
