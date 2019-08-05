from django.conf.urls import include, url
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

app_name = 'pages'

urlpatterns = format_suffix_patterns(
    [
        # Information page
        url(
            r'^info$',
            views.InfoPageView.as_view(),
            name='info',
        ),
    ]
)
