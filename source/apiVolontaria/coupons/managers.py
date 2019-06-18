from django.conf import settings
from django.core.mail import EmailMessage
from django.db import models
from django.core.paginator import Paginator
from django.test import override_settings

from .wc_api import WooCommerceAPI


class CouponOpManager(models.Manager):
    @staticmethod
    def set_status(queryset, status):
        for obj in queryset:
            obj.set_status(status)

    @staticmethod
    def batch_added_to_wc(queryset):
        paginator = Paginator(queryset.filter(coupon__coupon_wc_id__isnull=False, added_to_wc=False), 100)

        data_batch = {'update': []}

        wc_api = WooCommerceAPI()

        for index in range(0, paginator.num_pages):
            filter_queryset = paginator.page(index + 1).object_list

            if len(filter_queryset):
                for index, coupon_op in enumerate(filter_queryset):
                    try:

                        # Must package the update section, must first retrieve the remaining amounts of the coupon

                        wc_coupon_data = wc_api.get_coupon(coupon_op.coupon.code)
                        wc_amount = wc_coupon_data['amount']
                        print(coupon_op.coupon.code)
                        print(wc_amount)

                        data_coupon = {
                            'id': coupon_op.coupon.coupon_wc_id,
                            'amount': float(wc_amount) + coupon_op.amount,
                        }

                        data_batch['update'].append(data_coupon)
                    except Exception as e:
                        print('%s\nProblem batching update for %s, skipping' % (e, coupon_op.coupon))

        data_rep = wc_api.get_api().post("coupons/batch", data_batch).json()

        print(data_rep)

        if 'update' in data_rep:
            for data_item in data_rep['update']:
                coupon_op = queryset.filter(coupon__coupon_wc_id=data_item['id']).first()
                if coupon_op and 'error' not in data_item:
                    coupon_op.added_to_wc = True
                    coupon_op.save()
                    print('%s Completed' % coupon_op)
                    # {'error': {'code': 'woocommerce_rest_shop_coupon_invalid_id',
                    #            'data': {'status': 400},
                    #            'message': 'Identifiant non valide.'},
                    #  'id': 200303}

        return data_rep


class CouponManager(models.Manager):
    @staticmethod
    def set_status(queryset, status):
        for obj in queryset:
            obj.set_status(status)

    @staticmethod
    def generate_batch_coupons(queryset):
        paginator = Paginator(queryset.filter(coupon_wc_id__isnull=True).order_by('pk'), 100)

        for index in range(0, paginator.num_pages):
            filter_queryset = paginator.page(index + 1).object_list

            if len(filter_queryset):
                wc_api = WooCommerceAPI()
                data_rep = wc_api.create_batch_coupons(filter_queryset)

                for index, coupon in enumerate(filter_queryset):
                    id = data_rep['create'][index].get('id', None)

                    # {'id': 0,
                    # 'error': {'code': 'woocommerce_rest_coupon_code_already_exists',
                    # 'message': 'Ce code promotionnel existe déjà',
                    # 'data': {'status': 400}}}

                    # If coupon already exist, we re-associate the wc id to the field
                    if not id:
                        id = wc_api.get_coupon(coupon.code).get('id', None)

                    if id is not 0:
                        coupon.coupon_wc_id = id
                        coupon.coupon_wc_log = data_rep['create'][index]
                        coupon.save()
                        print('CREATED OR RETREIVED %s' % id)
                    else:
                        print('Coupon already exist, aborting...')


    @staticmethod
    def delete_batch_coupons(queryset):
        paginator = Paginator(queryset.order_by('pk'), 100)

        for index in range(0, paginator.num_pages):
            filter_queryset = paginator.page(index + 1).object_list

            if len(filter_queryset):
                wc_api = WooCommerceAPI()
                data_rep = wc_api.delete_batch_coupons(filter_queryset)

                print(data_rep)

                if len(data_rep):
                    for index, data_item in enumerate(data_rep['delete']):
                        coupon = queryset.get(coupon_wc_id=data_item['id'])
                        coupon.delete()
