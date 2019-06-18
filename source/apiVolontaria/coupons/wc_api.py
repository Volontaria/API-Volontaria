from decimal import Decimal

from django.conf import settings
from woocommerce import API


class WooCommerceAPI(object):

    def get_api(self):
        wcapi = API(
            url="https://nousrire.com",
            consumer_key=settings.WOOCOMERCE_API['key'],
            consumer_secret=settings.WOOCOMERCE_API['secret'],
            wp_api=True,
            version="wc/v3",
            timeout=60,
        )

        return wcapi

    def get_coupons(self, id=None):
        api = self.get_api()

        string = "coupons"
        if id:
            string = "%s/%s" % (string, id)

        response = api.get(string)

        return response

    def get_coupon(self, code):
        api = self.get_api()

        string = "coupons?code=%s" % code

        response = api.get(string)

        if response.status_code == 200:
            rep = response.json()[0]
            return rep

        return {}

    def get_coupons_list(self, id_list=[]):
        api = self.get_api()

        string = "coupons?per_page=100"

        response = api.get(string)

        if response.status_code == 200:
            rep = response.json()
            print(len(rep))
            return rep

        return {}

    def build_data_from_coupon(self, coupon, action):
        if action == 'create':
            data = {
                'code': '%s' % coupon.code,
                'amount': 0, #coupon.amount,
                'post_status': 'publish',
                'post_parent': '0',
                'menu_order': '0',
                'discount_type': 'smart_coupon',
                'free_shipping': False,
                'individual_use': False,
                'exclude_sale_items': False,
            }
        else:
            data = coupon.coupon_wc_id

        return data

    def create_single_coupon(self, code):
        api = self.get_api()

        data_coupon = {
                'code': '%s' % code,
                'amount': '0',
                'post_status': 'publish',
                'post_parent': '0',
                'menu_order': '0',
                'discount_type': 'smart_coupon',
                'free_shipping': False,
                'individual_use': False,
                'exclude_sale_items': False,
            }

        data_rep = api.post("coupons", data_coupon).json()

        return data_rep

    def get_coupon_current_amount(self, code):
        api = self.get_api()

        wc_coupon_data = self.get_coupon(code)
        if 'amount' in wc_coupon_data:
            return wc_coupon_data['amount']

        return 0

    def update_single_coupon(self, coupon_op):
        api = self.get_api()

        wc_amount = self.get_coupon_current_amount(coupon_op.coupon.code)

        new_amount = Decimal(wc_amount) + coupon_op.amount

        if new_amount < 0:
            new_amount = 0

        data_coupon = {
            'amount': str(new_amount),
        }

        data_rep = api.put("coupons/%s" % coupon_op.coupon.coupon_wc_id, data_coupon).json()

        return data_rep

    def delete_single_coupon(self, id):
        api = self.get_api()

        data = api.delete("coupons/%s?force=true" % id).json()

        return data

    def batch_coupon(self, coupons_obj_q, action='create'):
        if action not in ['create', 'delete']:
            print('Must use create or delete')
            return {}

        api = self.get_api()

        data_batch = {action: []}

        for coupon_obj in coupons_obj_q:
            data_coupon = self.build_data_from_coupon(coupon_obj, action)

            data_batch[action].append(data_coupon)

        data_rep = api.post("coupons/batch", data_batch).json()

        return data_rep

    def create_batch_coupons(self, coupons_data):
        return self.batch_coupon(coupons_data, 'create')

    def update_batch_coupons(self, coupon_ops):

        action = 'update'
        api = self.get_api()

        data_batch = {action: []}

        for coupon_op in coupon_ops:
            data_coupon = {
                'id': coupon_op.coupon_wc_id,
                'amount': 123,
            }

            data_batch[action].append(data_coupon)

        data_rep = api.post("coupons/batch", data_batch).json()

        return data_rep

    def delete_batch_coupons(self, coupons_data):
        return self.batch_coupon(coupons_data, 'delete')

    def get_order(self, id):
        api = self.get_api()

        string = "orders"
        if id:
            string = "%s/%s" % (string, id)

        response = api.get(string)

        print(response.json())

        return response
