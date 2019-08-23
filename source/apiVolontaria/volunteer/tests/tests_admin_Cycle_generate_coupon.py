from datetime import timedelta

from django.contrib.auth.models import User
from django.contrib.admin import ACTION_CHECKBOX_NAME
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITransactionTestCase

from django.contrib.admin.sites import AdminSite
from django.test import Client

from apiVolontaria.models import Profile
from location.models import Country, StateProvince, Address

from coupons.models import Coupon, CouponOperation
from ..admin import CycleAdmin
from ..models import Participation, Cell, Cycle, TaskType, Event


class CycleAdminGenerateCoupons(APITransactionTestCase):

    def create_user(self):
        self.username = "test_admin"
        self.password = User.objects.make_random_password()
        user, created = User.objects.get_or_create(username=self.username)
        user.set_password(self.password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()
        self.user = user

        profile = Profile(
            user=user,
            phone='1234567890',
            mobile='0987654321',
        )

        profile.save()

    def setUp(self):
        self.create_user()

        self.random_country = Country.objects.create(
            name="random country",
            iso_code="RC",
        )
        self.random_state_province = StateProvince.objects.create(
            name="random state",
            iso_code="RS",
            country=self.random_country,
        )
        self.address = Address.objects.create(
            address_line1='random address 1',
            postal_code='RAN DOM',
            city='random city',
            state_province=self.random_state_province,
            country=self.random_country,
        )
        self.cell = Cell.objects.create(
            name="my cell",
            address=self.address,
        )
        self.cycle = Cycle.objects.create(
            name="my cycle",
        )
        self.task_type = TaskType.objects.create(
            name="my tasktype",
        )

        self.start_date = timezone.now() - timezone.timedelta(
            minutes=100,
        )
        self.end_date = self.start_date + timezone.timedelta(
            minutes=50,
        )

        self.cycle_inactive = Cycle.objects.create(
            name="my cycle",
            start_date=self.start_date,
            end_date=self.end_date,
        )

        self.other_cycle = Cycle.objects.create(
            name="my other cycle",
            start_date=self.start_date,
            end_date=self.end_date,
        )

        # Some date INSIDE the cycle range
        self.start_date = self.start_date + timezone.timedelta(
            minutes=1,
        )
        self.end_date = self.end_date - timezone.timedelta(
            minutes=1,
        )

        self.event = Event.objects.create(
            cell=self.cell,
            cycle=self.cycle,
            task_type=self.task_type,
            start_date=self.start_date,
            end_date=self.end_date,
        )

        self.event2 = Event.objects.create(
            cell=self.cell,
            cycle=self.cycle,
            task_type=self.task_type,
            start_date=self.start_date,
            end_date=self.end_date,
        )

        self.participation = Participation(
            event=self.event,
            user=self.user,
            standby=False,
            presence_status='P',
        )
        self.participation.save()

        self.participation2 = Participation(
            event=self.event2,
            user=self.user,
            standby=False,
            presence_status='P',
        )
        self.participation2.save()

        self.site = AdminSite()
        self.admin = CycleAdmin(Cycle, self.site)

        self.profile = Profile.objects.filter(
            user__pk=self.participation.user.pk,
        ).first()

        self.client = Client()
        self.client.login(username=self.username, password=self.password)

    def test_admin_cycle_generate_coupons(self):
        """
        Ensure that we can generate coupons
        """

        change_url = reverse('admin:volunteer_cycle_changelist')

        data = {'action': 'generate_coupons',
                ACTION_CHECKBOX_NAME: [self.cycle.pk, ]}

        response = self.client.post(change_url, data, follow=True)

        self.assertEquals(response.status_code, 200)

        coupons = Coupon.objects.all()
        coupons_op = CouponOperation.objects.all()

        self.assertEquals(len(coupons), 1)
        self.assertEquals(len(coupons_op), 1)

    def test_admin_cycle_generate_coupons_multiple_cycles_selected(self):

        change_url = reverse('admin:volunteer_cycle_changelist')

        data = {'action': 'generate_coupons',
                ACTION_CHECKBOX_NAME: [self.cycle.pk, self.other_cycle.pk,]}

        response = self.client.post(change_url, data, follow=True)

        self.assertEquals(response.status_code, 200)

        coupons = Coupon.objects.all()
        coupons_op = CouponOperation.objects.all()

        self.assertEquals(len(coupons), 0)
        self.assertEquals(len(coupons_op), 0)

    def test_admin_cycle_generate_coupons_blocked_by_init_participation(self):
        """
        Ensure that we cannot generate this cycle coupons if
        there is Participation in the Initialisation state associated to that cycle
        """

        self.event3 = Event.objects.create(
            cell=self.cell,
            cycle=self.cycle,
            task_type=self.task_type,
            start_date=self.start_date,
            end_date=self.end_date,
        )

        self.participation3 = Participation(
            event=self.event3,
            user=self.user,
            standby=False,
            presence_status='I',
        )
        self.participation3.save()

        change_url = reverse('admin:volunteer_cycle_changelist')

        data = {'action': 'generate_coupons',
                ACTION_CHECKBOX_NAME: [self.cycle.pk, ]}

        response = self.client.post(change_url, data, follow=True)

        self.assertEquals(response.status_code, 200)

        coupons = Coupon.objects.all()
        coupons_op = CouponOperation.objects.all()

        self.assertEquals(len(coupons), 0)
        self.assertEquals(len(coupons_op), 0)

    def test_admin_cycle_generate_coupons_existing_coupons(self):
        """
        Ensure that we cannot generate this cycle coupons if
        there is already a CouponOperation associated to that cycle
        """

        # Manually create the coupon
        coupon = Coupon.objects.create(
            user=self.user,
            code=Coupon.generate_unique_code(self.user)
        )

        # Manually create the coupon operation
        coupon_op = CouponOperation.objects.create(
            coupon=coupon,
            amount=100,
            cycle=self.cycle,
        )

        change_url = reverse('admin:volunteer_cycle_changelist')

        data = {'action': 'generate_coupons',
                ACTION_CHECKBOX_NAME: [self.cycle.pk, ]}

        response = self.client.post(change_url, data, follow=True)

        self.assertEquals(response.status_code, 200)

        coupons = Coupon.objects.all()
        coupons_op = CouponOperation.objects.all()

        # We have only the initially created coupon and couponOperation
        self.assertEquals(len(coupons), 1)
        self.assertEquals(len(coupons_op), 1)

    def test_admin_cycle_generate_coupons_no_participation(self):
        """
        Ensure that we cannot generate this cycle coupons if
        there is no Participation associated to that cycle
        """

        change_url = reverse('admin:volunteer_cycle_changelist')

        data = {'action': 'generate_coupons',
                ACTION_CHECKBOX_NAME: [self.other_cycle.pk, ]}

        response = self.client.post(change_url, data, follow=True)

        self.assertEquals(response.status_code, 200)

        coupons = Coupon.objects.all()
        coupons_op = CouponOperation.objects.all()

        self.assertEquals(len(coupons), 0)
        self.assertEquals(len(coupons_op), 0)
