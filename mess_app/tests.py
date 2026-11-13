from datetime import date
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .models import User, LeaveRequest, Bill


class BillingTest(TestCase):
    def setUp(self):
        # Runs before every test: create a student with no mobile number,
        # so the Twilio/WhatsApp code never runs
        self.student = User.objects.create_user(
            username="teststudent", password="testpass123"
        )

    def make_bill(self):
        # April 2026 has 30 days, rate Rs 100/day
        return Bill.objects.create(
            student=self.student,
            month=date(2026, 4, 1),
            base_rate_per_day=Decimal("100.00"),
            total_days_in_month=30,
            last_date_of_payment=date(2026, 4, 10),
        )

    def test_approved_leave_reduces_bill(self):
        # 5 to 8 April = 4 days approved
        LeaveRequest.objects.create(
            student=self.student,
            from_date=date(2026, 4, 5),
            to_date=date(2026, 4, 8),
            reason="Home visit",
            status="A",
        )
        bill = self.make_bill()

        # By hand: 100 x 30 = 3000, minus 100 x 4 = 400, total 2600
        self.assertEqual(bill.leave_days_approved, 4)
        self.assertEqual(bill.base_amount, Decimal("3000.00"))
        self.assertEqual(bill.adjustment_amount, Decimal("400.00"))
        self.assertEqual(bill.total_amount, Decimal("2600.00"))

    def test_pending_leave_is_not_deducted(self):
        LeaveRequest.objects.create(
            student=self.student,
            from_date=date(2026, 4, 5),
            to_date=date(2026, 4, 8),
            reason="Home visit",
            status="P",  # still pending
        )
        bill = self.make_bill()

        self.assertEqual(bill.leave_days_approved, 0)
        self.assertEqual(bill.total_amount, Decimal("3000.00"))

    def test_leave_crossing_month_counts_only_april_days(self):
        # 29 March to 3 April: only 1, 2, 3 April belong to April = 3 days
        LeaveRequest.objects.create(
            student=self.student,
            from_date=date(2026, 3, 29),
            to_date=date(2026, 4, 3),
            reason="Festival",
            status="A",
        )
        bill = self.make_bill()

        self.assertEqual(bill.leave_days_approved, 3)
        self.assertEqual(bill.total_amount, Decimal("2700.00"))


class RBACTest(TestCase):
    def setUp(self):
        self.student = User.objects.create_user(
            username="rbacstudent", password="testpass123", role=User.STUDENT
        )
        self.staff = User.objects.create_user(
            username="rbacstaff", password="testpass123",
            role=User.ADMIN, is_staff=True, is_superuser=True,
        )

    def test_anonymous_redirected_from_student_dashboard(self):
        response = self.client.get(reverse("student_dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    def test_student_blocked_from_django_admin(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("admin:index"))
        self.assertEqual(response.status_code, 302)

    def test_staff_can_open_django_admin(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse("admin:index"))
        self.assertEqual(response.status_code, 200)