import os

from django.conf import settings
from django.core.management.base import BaseCommand
from coupons import models
from coupons.wc_api import WooCommerceAPI

CHECK_FILE_PATH = path = "%s/THREAD_STATUS" % settings.BASE_DIR


class Command(BaseCommand):
    help = 'Manage the coupons mechanics'

    def handle(self, *args, **options):
        try:
            if not os.path.exists(CHECK_FILE_PATH):
                with open(CHECK_FILE_PATH, 'w') as f:
                    f.write('unlocked')

            if ask_thread_lock(True):
                wc_api = WooCommerceAPI()
                print('---COUPON---')
                coupon_query = models.RechargeableCoupon.objects.filter(status__isnull=False)

                for coupon in coupon_query:
                    # CREATE RECHARGEABLE COUPON
                    if coupon.status == '1':
                        coupon.create_wc_coupon(wc_api)

                    # DELETE RECHARGEBLE COUPON
                    elif coupon.status == '2':
                        coupon.delete_wc_coupon(wc_api)

                print('---COUPON OPERATIONS---')
                coupon_op_query = models.CouponOperation.objects.filter(status__isnull=False, coupon__coupon_wc_id__isnull=False)

                for coupon_op in coupon_op_query:
                    status = coupon_op.status
                    if status in ['1', '3']:
                        # DO TRANSACTION TO WC

                        data_rep = coupon_op.add_amount_to_wc(wc_api, send_email=status == '1')

                        # Will send the email if status ask for
                        if status == '1' and not coupon_op.email_sended:
                            coupon_op.send_email()
                    # SEND EMAIL
                    elif coupon_op.status == '2':
                        coupon_op.send_email()

                ask_thread_lock(False)
            else:
                print("Thread already existing ! Aborting...")

        except Exception as e:
            print("Error, aborting and unlocking...")
            print(e)
            ask_thread_lock(False)


def ask_thread_lock(lock=True):
    try:
        value = open(CHECK_FILE_PATH, 'r').read().splitlines()[0]

        if lock and value in ['', 'unlocked']:
            wf = open(path, 'w')
            wf.write('locked')
            wf.close()
            print("thread_status: %s" % value)
            return True
        elif not lock:
            wf = open(path, 'w')
            wf.write('unlocked')
            wf.close()
            print("thread_status: %s" % value)
            return True
        else:
            print(lock)
            print(value)
            print("No valid cases...")
            return False
    except Exception as e:
        print(e)
        return False
