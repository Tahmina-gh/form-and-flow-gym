from datetime import timedelta
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from . import models as m, services as s

class GymTests(TestCase):
    def setUp(self):
        self.plan = m.Plan.objects.create(name='P', price_monthly=10, price_yearly=100)
        self.t = m.Trainer.objects.create(name='T', specialization='Strength')
        self.gc = m.GymClass.objects.create(name='Strength', trainer=self.t, start=timezone.now() + timedelta(days=1), capacity=1)
        self.u1 = self._member('a'); self.u2 = self._member('b')
    def _member(self, n):
        u = m.User.objects.create_user(n, f'{n}@x.com', 'pw12345678')
        today = timezone.localdate(); m.Membership.objects.create(user=u, plan=self.plan, cycle='monthly', start=today, end=today + timedelta(days=30), status='active'); return u

    def test_capacity_waitlist_and_promotion(self):
        s.book_class(self.u1, self.gc.pk); _, msg = s.book_class(self.u2, self.gc.pk)
        self.assertIn('waitlist', msg); self.assertTrue(self.gc.is_full)
        s.cancel_booking(self.u1, self.gc.pk)
        self.assertEqual(m.Booking.objects.get(user=self.u2).status, 'booked')
        self.assertTrue(m.Notification.objects.filter(user=self.u2).exists())
    def test_no_duplicate_booking(self):
        s.book_class(self.u1, self.gc.pk); _, msg = s.book_class(self.u1, self.gc.pk)
        self.assertIn('already', msg); self.assertEqual(m.Booking.objects.count(), 1)
    def test_booking_requires_membership(self):
        u = m.User.objects.create_user('c', 'c@x.com', 'pw12345678'); _, msg = s.book_class(u, self.gc.pk)
        self.assertIn('membership', msg)
    def test_trainer_double_booking_blocked(self):
        st = timezone.now() + timedelta(days=2); self.client.login(username='a', password='pw12345678')
        self.client.post(reverse('book_trainer', args=[self.t.pk]), {'slot': st.isoformat()})
        self.client.login(username='b', password='pw12345678')
        self.client.post(reverse('book_trainer', args=[self.t.pk]), {'slot': st.isoformat()})
        self.assertEqual(m.TrainerSession.objects.count(), 1)
    def test_purchase_then_admin_confirm_activates(self):
        u = m.User.objects.create_user('d', 'd@x.com', 'pw12345678'); self.client.login(username='d', password='pw12345678')
        self.client.post(reverse('buy_plan', args=[self.plan.pk]), {'cycle': 'yearly'})
        p = m.Payment.objects.get(user=u); self.assertEqual(p.status, 'pending'); self.assertIsNone(u.active_membership)
        staff = m.User.objects.create_user('boss', 'b@x.com', 'pw12345678', role='admin'); self.client.login(username='boss', password='pw12345678')
        self.client.post(reverse('confirm_payment', args=[p.pk])); self.assertIsNotNone(m.User.objects.get(pk=u.pk).active_membership)
    def test_member_cannot_open_admin_pages(self):
        self.client.login(username='a', password='pw12345678')
        for name in ('manage', 'checkin'): self.assertEqual(self.client.get(reverse(name)).status_code, 302)
    def test_dashboard_needs_login(self): self.assertEqual(self.client.get(reverse('dashboard')).status_code, 302)
    def test_trial_lead_saved_and_honeypot(self):
        data = {'name': 'N', 'email': 'n@x.com', 'phone': '+92 300 1234567', 'age': 30, 'goal': 'x', 'level': 'beginner'}
        self.client.post(reverse('trial'), data); self.assertEqual(m.Lead.objects.count(), 1)
        self.client.post(reverse('trial'), {**data, 'website': 'spam'}); self.assertEqual(m.Lead.objects.count(), 1)
    def test_checkin_and_duplicate_scan(self):
        staff = m.User.objects.create_user('boss', 'b@x.com', 'pw12345678', role='admin'); self.client.login(username='boss', password='pw12345678')
        self.client.post(reverse('checkin'), {'code': self.u1.member_code}); self.client.post(reverse('checkin'), {'code': self.u1.member_code})
        self.assertEqual(m.Attendance.objects.filter(user=self.u1).count(), 1)
    def test_signup_login_pages_and_public_pages(self):
        r = self.client.post(reverse('signup'), {'username': 'new', 'email': 'new@x.com', 'first_name': 'N', 'phone': '', 'password1': 'Sup3rSecret!x', 'password2': 'Sup3rSecret!x'})
        self.assertEqual(r.status_code, 302); self.assertTrue(any('Verify' in x.subject for x in mail.outbox))
        for name in ('home', 'classes', 'login', 'signup', 'trial', 'tour', 'contact', 'quiz', 'password_reset'): self.assertEqual(self.client.get(reverse(name)).status_code, 200, name)
        self.assertEqual(self.client.get(f'/api/classes/{self.gc.pk}/availability/').json()['capacity'], 1)
