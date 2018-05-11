from django.conf.urls import include, url
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = format_suffix_patterns(
    [
        # Faqs
        url(
            r'^$',
            views.FaqCategory.as_view(),
            name='faqs_category',
        ),
        url(
            r'^(?P<pk>\d+)$',
            views.FaqCategoryId.as_view(),
            name='faqs_category_id',
        ),
    ]
)
