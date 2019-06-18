# -*- coding: utf-8 -*-

from django.contrib import admin
from django.db import models
from django.forms import Textarea
from django.utils.html import format_html

from .models import RechargeableCoupon, CouponOperation, Coupon


class CouponOperationInline(admin.TabularInline):
    model = CouponOperation
    extra = 0

    FIELDS = ('cycle', 'amount', 'wc_amount_total', 'wc_added_date', 'status', 'email_sended', 'added_to_wc', 'note', )

    fields = FIELDS
    readonly_fields = ('cycle', 'amount', 'wc_amount_total', 'wc_added_date', 'status', 'email_sended', 'added_to_wc', )

    def has_add_permission(self, request, obj):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 50})},
    }


class CouponOperationAdmin(admin.ModelAdmin):
    list_display = [
        'added_to_wc',
        'email_sended',
        'coupon',
        'cycle',
        'amount',
        'wc_amount_total',
        'status',
        'wc_added_date',
        'show_wc_url',
        'note',
    ]

    list_display_links = ('coupon', )

    fields = (
        'coupon',
        'cycle',
        'added_to_wc',
        'email_sended',
        'amount',
        'status',
        'wc_amount_total',
        'wc_added_date',
        'show_wc_url',
        'note',
        'coupon_wc_log',
    )

    readonly_fields = [
        'email_sended',
        'added_to_wc',
        'status',
        'wc_amount_total',
        'wc_added_date',
        'show_wc_url',
        'coupon_wc_log',
    ]

    actions = (
        'safe_delete',
        'resend_coupon_email',
    )

    list_filter = (
        'cycle',
        'email_sended',
        'added_to_wc',
        'status',
    )

    search_fields = (
        'coupon__code',
        'coupon__user__email',
        'coupon__user__username',
        'coupon__user__first_name',
        'coupon__user__last_name',
        'coupon__coupon_wc_id',
    )

    date_hierarchy = 'wc_added_date'

    raw_id_fields = ('coupon',)

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ['amount', 'coupon', 'cycle', ]
        return self.readonly_fields

    def resend_coupon_email(self, request, queryset):
        CouponOperation.objects.set_status(queryset, '2')

    resend_coupon_email.short_description = \
        u"Envoyer le(s) courriel(s)"

    def safe_delete(self, request, queryset):
        for obj in queryset:
            if not obj.added_to_wc:
                obj.delete()

    safe_delete.short_description = \
        u"Suprimer le(s) opération(s) si pas sur WC"

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    @staticmethod
    def show_wc_url(obj):
        url = obj.coupon.wc_url()
        if url:
            return format_html("<a href='%s'target='_blank'>See Coupon</a>" % url)
        return None

    show_wc_url.mark_safe = True


admin.site.register(CouponOperation, CouponOperationAdmin)


class RechargeableCouponAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'code',
        'coupon_wc_id',
        'status',
        'show_wc_url',
    ]

    list_display_links = [
        'code',
    ]

    inlines = [CouponOperationInline, ]

    fields = [
        'user',
        'code',
        'show_wc_url',
        'coupon_wc_id',
        'status',
        'coupon_wc_log',
    ]

    list_filter = (
        'status',
    )

    readonly_fields = [
        'code',
        'coupon_wc_log',
        'coupon_wc_id',
        'show_wc_url',
        'status',
    ]

    search_fields = [
        'code',
        'user__first_name',
        'user__last_name',
        'user__email',
        'coupon_wc_id',
    ]

    raw_id_fields = ('user',)

    actions = (
        'delete_wc_coupons',
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ['user', ]
        return self.readonly_fields

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def delete_wc_coupons(self, request, queryset):
        RechargeableCoupon.objects.set_status(queryset, '2')

    delete_wc_coupons.short_description = \
        "Supprimer le(s) coupon(s) ici et sur WC"

    @staticmethod
    def user__email(obj):
        return obj.user.email

    @staticmethod
    def user__first_name(obj):
        return obj.user.first_name

    @staticmethod
    def user__last_name(obj):
        return obj.user.last_name

    @staticmethod
    def show_wc_url(obj):
        url = obj.wc_url()
        if url:
            return format_html("<a href='%s'target='_blank'>See Coupon</a>" % url)
        return None

    show_wc_url.mark_safe = True


admin.site.register(RechargeableCoupon, RechargeableCouponAdmin)


class CouponAdmin(admin.ModelAdmin):
    list_display = [
        'email_sended',
        'cycle',
        'code',
        'amount',
        'coupon_wc_id',
        'user__email',
    ]

    list_display_links = [
        'code',
    ]

    readonly_fields = [
        'code',
        'coupon_wc_id',
        'email_sended',
        'coupon_wc_log',
    ]

    search_fields = [
        'code',
        'user__first_name',
        'user__last_name',
        'user__email',
    ]

    list_filter = [
        'cycle',
        'email_sended',
    ]

    raw_id_fields = ('user',)

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ['presence_duration_minutes', 'user', 'cycle', ]
        return self.readonly_fields

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_actions(self, request):
        actions = super(CouponAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    @staticmethod
    def user__email(obj):
        return obj.user.email

    @staticmethod
    def user__first_name(obj):
        return obj.user.first_name

    @staticmethod
    def user__last_name(obj):
        return obj.user.last_name


admin.site.register(Coupon, CouponAdmin)
