from django.contrib import admin
from orderable.admin import OrderableAdmin

from . import models


class FaqCategoryAdmin(OrderableAdmin):
    list_display = ('sort_order_display', 'is_active', 'title',)
    list_display_links = ('title',)
    list_editable = ('is_active',)

    fieldsets = (
        (u'General', {
            'fields': ('is_active', 'title',)
        }),
    )

    search_field = [
        'title',
        'content',
    ]


class FaqAdmin(OrderableAdmin):
    list_display = ('sort_order_display', 'is_active', 'category', 'title', )
    list_display_links = ('title', )
    list_editable = ('is_active',)

    fieldsets = (
        (u'General', {
            'fields': ('is_active', 'category', 'title', 'content', )
        }),
    )

    search_fields = [
        'title',
        'content',
    ]

    list_filter = [
        'category',
    ]

admin.site.register(models.FaqCategory, FaqCategoryAdmin)
admin.site.register(models.Faq, FaqAdmin)
