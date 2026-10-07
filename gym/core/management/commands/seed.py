import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from core import models as m

class Command(BaseCommand):
    help = 'DEMO DATA ONLY - never run on production. Creates plans, trainers, classes, members.'
    def handle(self, *a, **k):
        U = m.User
        if not U.objects.filter(username='admin').exists():
            U.objects.create_superuser('admin', 'admin@example.com', 'admin12345', role='admin')
        plans = []
        for n, mo, yr, cl, pt, gp, rec, feat, ben in [
            ('Essential', 79, 790, 8, 0, 1, False, False, 'Studio access\n8 classes a month\nGuest pass monthly'),
            ('Balance', 129, 1290, 0, 1, 2, True, True, 'Unlimited classes\nRecovery zone\n1 coaching session'),
            ('Signature', 199, 1990, 0, 2, 4, True, False, 'Everything in Balance\n2 private sessions\nPersonal programming')]:
            plans.append(m.Plan.objects.get_or_create(name=n, defaults=dict(price_monthly=mo, price_yearly=yr, classes_per_month=cl, pt_sessions=pt, guest_passes=gp, recovery_access=rec, featured=feat, benefits=ben, description=f'{n} membership'))[0])
        trainers = [m.Trainer.objects.get_or_create(name=n, defaults=dict(specialization=s, years=y, bio=f'{n} coaches {s.lower()}.'))[0]
                    for n, s, y in [('Elena', 'Pilates & Mobility', 8), ('Marcus', 'Strength', 10), ('Sofia', 'Yoga & Pilates', 6), ('Jordan', 'HIIT & Functional', 7), ('Amir', 'Strength & Conditioning', 5)]]
        now = timezone.now().replace(minute=0, second=0, microsecond=0)
        if not m.GymClass.objects.exists():
            for d in range(1, 8):
                for name, hr in [('Pilates', 7), ('Yoga', 9), ('Strength', 18), ('HIIT', 19), ('Mobility', 12)]:
                    m.GymClass.objects.create(name=name, trainer=random.choice(trainers), start=(now + timedelta(days=d)).replace(hour=hr), capacity=random.choice([6, 10, 12]))
        for i in range(1, 11):
            u, made = U.objects.get_or_create(username=f'member{i}', defaults=dict(email=f'member{i}@example.com', first_name=f'Member{i}', email_verified=True))
            if made:
                u.set_password('member12345'); u.save()
                p = random.choice(plans); today = timezone.localdate()
                m.Membership.objects.create(user=u, plan=p, cycle='monthly', start=today, end=today + timedelta(days=30), status='active')
                m.Payment.objects.create(user=u, amount=p.price_monthly, status='paid')
                for d in range(random.randint(1, 6)): m.Attendance.objects.create(user=u, check_in=now - timedelta(days=d))
        for n, q in [('Amara', 'The first studio that made me look forward to Tuesday mornings.'), ('Raj', 'My coach adjusted my program the moment my knee acted up.'), ('Lina', 'The recovery zone alone is worth the membership.')]:
            m.Testimonial.objects.get_or_create(name=n, defaults=dict(quote=q, published=True))
        self.stdout.write(self.style.SUCCESS('Seeded. Admin: admin / admin12345 | members: member1..10 / member12345'))
