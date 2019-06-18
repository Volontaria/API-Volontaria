from django.contrib import admin
from orderable.admin import OrderableAdmin
from reversion.admin import VersionAdmin

from pages.models import InfoSection


@admin.register(InfoSection)
class InfoSectionAdmin(OrderableAdmin, VersionAdmin):
    list_display = ('sort_order_display', 'is_active', 'is_accordion', 'title')
    list_display_links = ('title',)
    list_editable = ('is_active', 'is_accordion')

    fields = ('is_active', 'is_accordion', 'title', 'content', )

    search_fields = ('content', 'title', )
