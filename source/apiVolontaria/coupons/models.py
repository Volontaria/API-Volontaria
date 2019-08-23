from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.db import models

from volunteer.models import Cycle

from coupons.wc_api import WooCommerceAPI
from .managers import CouponManager, CouponOpManager

AMOUNT_PER_HOUR = 5

COUPONS_STATUS = [
    ('1', 'wc_create'),
    ('2', 'wc_delete'),
]
COUPONS_OP_STATUS = [
    ('1', 'add_to_wc_send_email'),
    ('2', 'send_email'),
    ('3', 'add_to_wc_only'),
]


class Coupon(models.Model):
    code = models.CharField(
        verbose_name="Code",
        max_length=100,
        blank=True,
        unique=True,
    )
    user = models.OneToOneField(
        User,
        related_name='rechargeable_coupon',
        blank=False,
        null=True,
        on_delete=models.SET_NULL,
        unique=True
    )

    coupon_wc_id = models.PositiveIntegerField(null=True, blank=True, default=None)
    coupon_wc_log = models.TextField(null=True, blank=True, default='')
    status = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=COUPONS_STATUS,
        default='1'
    )

    objects = CouponManager()

    class Meta:
        verbose_name = 'Coupon Rechargeable'

    def __str__(self):
        try:
            return '{0} - {1} - [{2}]'.format(
                self.code,
                self.user.email,
                self.coupon_wc_id,
            )
        except:
            return '{0} - N/A - [{2}]'.format(
                self.code,
                self.coupon_wc_id,
            )

    @staticmethod
    def generate_unique_code(user):
        try:
            code_start = user.email.split('@')[0]
            user_id = user.pk
        except:
            code_start = "nousrire"
            user_id = 0

        return "%s-%s" % (
            code_start,
            user_id + 112
        )

    def set_status(self, status):
        if status == '1' and self.coupon_wc_id:
            return
        elif status == '2' and not self.coupon_wc_id:
            return

        self.status = status
        self.save()

    def clean(self):
        if not self.code:
            self.code = self.generate_unique_code(self.user)

        if Coupon.objects.exclude(id=self.id).filter(code=self.code):
            raise ValidationError('Coupon already exist !')

    def wc_url(self):
        if self.coupon_wc_id:
            return "https://nousrire.com/wp-admin/post.php?post=%s&action=edit" % self.coupon_wc_id

        return None
        
    def create_wc_coupon(self, wc_api=None):
        if not wc_api:
            wc_api = WooCommerceAPI()

        data_rep = wc_api.create_single_coupon(self.code)
        if 'id' in data_rep:
            id = self.coupon_wc_id = data_rep['id']
        else:
            id = wc_api.get_coupon(self.code).get('id', None)

        if id is not 0:
            print('CREATED OR RETRIEVED %s' % id)
            self.coupon_wc_id = id
            self.coupon_wc_log = data_rep
            self.status = None
            self.save()
        else:
            print('ERROR Creating Coupon!')
            if data_rep:
                self.coupon_wc_log = data_rep
                self.save()
            print('ERROR !')
    
    def delete_wc_coupon(self, wc_api=None):
        if not wc_api:
            wc_api = WooCommerceAPI()
        
        data_rep = wc_api.delete_single_coupon(self.coupon_wc_id)
        if 'id' in data_rep:
            print('DELETE %s' % data_rep['id'])
            self.delete()
        elif data_rep:
            self.delete()
            print('Seem to be not existing on WC, just delete')

    def get_balance(self):
        wc_api = WooCommerceAPI()
        data = wc_api.get_coupons(self.coupon_wc_id)

        if data.status_code == 200:
            try:
                return '%s $' % str(data.json()['amount'])
            except:
                pass

        return "N/A"


class CouponOperation(models.Model):
    coupon = models.ForeignKey(Coupon, null=True, on_delete=models.CASCADE)

    cycle = models.ForeignKey(
        Cycle,
        verbose_name="Cycle",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    note = models.TextField(blank=True, null=True)

    amount = models.DecimalField(decimal_places=2, max_digits=8, blank=False, null=False)

    email_sended = models.BooleanField(default=False)
    added_to_wc = models.BooleanField(default=False)
    wc_amount_total = models.DecimalField(decimal_places=2, max_digits=8, blank=True, null=True)
    wc_added_date = models.DateTimeField(blank=True, null=True)
    coupon_wc_log = models.TextField(null=True, blank=True, default='')

    status = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=COUPONS_OP_STATUS,
        default='3'
    )

    objects = CouponOpManager()

    class Meta:
        verbose_name = 'Opération'
        ordering = ('-pk', )

    def __str__(self):
        return '{0} - {1}min'.format(
            self.coupon.user.email,
            self.amount,
        )

    def set_status(self, status):
        if status == '1' and self.added_to_wc:
            return

        self.status = status
        self.save()

    @staticmethod
    def get_amount_from_minute(presence_duration_minutes):
        return round(presence_duration_minutes / 60 * AMOUNT_PER_HOUR, 2)

    def add_amount_to_wc(self, wc_api=None, send_email=False):
        if not wc_api:
            wc_api = WooCommerceAPI()
        if not self.added_to_wc:
            data_rep = wc_api.update_single_coupon(self)

            if data_rep:
                self.coupon_wc_log = data_rep
                self.save()

                if 'id' in data_rep:
                    print('TRANSACTION TO WC %s' % self.coupon.code)
                    self.added_to_wc = True
                    if send_email:
                        self.status = '2'
                    else:
                        self.status = ''
                    self.wc_added_date = datetime.now()
                    self.save()

                    if 'amount' in data_rep:
                        self.wc_amount_total = data_rep['amount']
                        self.save()
                    else:
                        print('Error adding amount to wc, no amount in response' % data_rep)

                    return data_rep
                else:
                    print('Error adding amount to wc, no id in response %s' % data_rep)
        return None

    def send_email(self):
        if settings.COUPON_SEND_EMAIL:
            print('Sending Email to %s' % self.coupon.user.email)

            message = EmailMessage(
                to=[self.coupon.user.email, ]
            )

            message.from_email = None
            message.template_id = settings.ANYMAIL['TEMPLATES']['COUPON']  # "Coupon2019"
            message.merge_global_data = {

                'CODE': self.coupon.code,
                'AMOUNT': str(self.amount),
                'BALANCE': str(self.wc_amount_total),
                'YEAR': datetime.now().year
            }

            rep = message.send()

            if rep == 1:
                self.email_sended = True
                self.status = None
                self.save()
                print('Email sended!')
            else:
                print('Problem sending email status: %s' % rep)
        else:
            print('Simulating email to %s' % self.coupon.user.email)
