from django.contrib import admin

from .models import CKEditorPage


@admin.register(CKEditorPage)
class CKEditorPageAdmin(admin.ModelAdmin):
    readonly_fields = (
        'updated_at',
        'created_at'
    )
