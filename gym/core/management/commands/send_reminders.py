from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from core import models as m, services as s

class Command(BaseCommand):
    help = 'Run daily (PythonAnywhere Scheduled task): expire memberships, send expiry + class reminders.'
    def handle(self, *a, **k):
        today = timezone.localdate()
        for ms in m.Membership.objects.filter(status='active', end__lt=today): ms.status = 'expired'; ms.save(); s.notify(ms.user, 'Your membership has expired. Renew to keep your benefits.')
        for days in (30, 7, 1):
            for ms in m.Membership.objects.filter(status='active', end=today + timedelta(days=days)): s.notify(ms.user, f'Your membership expires in {days} day(s).')
        soon = timezone.now() + timedelta(hours=24)
        for b in m.Booking.objects.filter(status='booked', gym_class__start__range=(timezone.now(), soon)).select_related('user', 'gym_class'): s.notify(b.user, f'Reminder: {b.gym_class.name} at {b.gym_class.start:%H:%M}.')
        self.stdout.write('Reminders done.')
