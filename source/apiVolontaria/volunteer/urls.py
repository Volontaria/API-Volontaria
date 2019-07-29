from django.conf.urls import include, url
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

app_name = 'volunteer'

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
            r'^cells/(?P<pk>\d+)/export$',
            views.CellExport.as_view(),
            name='cell_export',
        ),
        url(
            r'^cells/(?P<pk>\d+)$',
            views.CellsId.as_view(),
            name='cells_id',
        ),
        # Events
        url(
            r'^events$',
            views.Events.as_view(),
            name='events',
        ),
        url(
            r'^events/(?P<pk>\d+)$',
            views.EventsId.as_view(),
            name='events_id',
        ),
        # Participations
        url(
            r'^participations$',
            views.Participations.as_view(),
            name='participations',
        ),
        url(
            r'^participations/(?P<pk>\d+)$',
            views.ParticipationsId.as_view(),
            name='participations_id',
        ),
    ]
)
