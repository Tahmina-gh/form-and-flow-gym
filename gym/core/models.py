import secrets
from datetime import timedelta
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Count, Q
from django.utils import timezone

def _code(): return secrets.token_hex(4).upper()

class User(AbstractUser):
    ROLES = [('member', 'Member'), ('trainer', 'Trainer'), ('admin', 'Admin')]
    role = models.CharField(max_length=10, choices=ROLES, default='member')
    phone = models.CharField(max_length=30, blank=True)
    photo = models.ImageField(upload_to='profiles/', blank=True)
    email_verified = models.BooleanField(default=False)
    member_code = models.CharField(max_length=8, unique=True, default=_code)
    @property
    def is_gym_admin(self): return self.is_superuser or self.role == 'admin'
    @property
    def active_membership(self):
        return self.memberships.filter(status='active', end__gte=timezone.localdate()).select_related('plan').first()

class Plan(models.Model):
    name = models.CharField(max_length=60); description = models.TextField(blank=True)
    price_monthly = models.DecimalField(max_digits=8, decimal_places=2)
    price_yearly = models.DecimalField(max_digits=8, decimal_places=2)
    classes_per_month = models.PositiveIntegerField(default=0, help_text='0 = unlimited')
    pt_sessions = models.PositiveIntegerField(default=0); guest_passes = models.PositiveIntegerField(default=0)
    recovery_access = models.BooleanField(default=False); benefits = models.TextField(blank=True, help_text='one per line')
    featured = models.BooleanField(default=False); active = models.BooleanField(default=True)
    def __str__(self): return self.name
    def benefit_list(self): return [b for b in self.benefits.splitlines() if b.strip()]

class Membership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memberships')
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    cycle = models.CharField(max_length=7, choices=[('monthly', 'Monthly'), ('yearly', 'Yearly')])
    start = models.DateField(); end = models.DateField()
    status = models.CharField(max_length=10, default='pending', choices=[('pending', 'Pending payment'), ('active', 'Active'), ('cancelled', 'Cancelled'), ('expired', 'Expired')])
    class Meta: ordering = ['-start']; indexes = [models.Index(fields=['user', 'status', 'end'])]
    def __str__(self): return f'{self.user} – {self.plan} ({self.status})'

class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    membership = models.ForeignKey(Membership, null=True, blank=True, on_delete=models.SET_NULL)
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    status = models.CharField(max_length=10, default='pending', choices=[('pending', 'Pending'), ('paid', 'Paid'), ('failed', 'Failed'), ('refunded', 'Refunded')])
    provider = models.CharField(max_length=20, default='manual', help_text='manual / stripe / jazzcash ...')
    transaction_id = models.CharField(max_length=64, unique=True, default=_code)
    created = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['-created']

class Trainer(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=80); specialization = models.CharField(max_length=120)
    bio = models.TextField(blank=True); years = models.PositiveIntegerField(default=1)
    certifications = models.CharField(max_length=200, blank=True)
    photo = models.ImageField(upload_to='trainers/', blank=True)
    session_price = models.DecimalField(max_digits=7, decimal_places=2, default=40)
    session_minutes = models.PositiveIntegerField(default=60)
    active = models.BooleanField(default=True)
    def __str__(self): return self.name

class GymClass(models.Model):
    name = models.CharField(max_length=80); description = models.TextField(blank=True)
    trainer = models.ForeignKey(Trainer, on_delete=models.PROTECT)
    start = models.DateTimeField(); duration_minutes = models.PositiveIntegerField(default=45)
    capacity = models.PositiveIntegerField(default=12)
    difficulty = models.CharField(max_length=12, default='All levels', choices=[(x, x) for x in ('All levels', 'Beginner', 'Intermediate', 'Advanced')])
    location = models.CharField(max_length=80, default='Main studio')
    active = models.BooleanField(default=True)
    class Meta: ordering = ['start']; verbose_name_plural = 'classes'
    def __str__(self): return f'{self.name} {self.start:%a %d %b %H:%M}'
    @property
    def booked(self): return self.bookings.filter(status='booked').count()
    @property
    def spots_left(self): return max(self.capacity - self.booked, 0)
    @property
    def is_full(self): return self.spots_left == 0

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    gym_class = models.ForeignKey(GymClass, on_delete=models.CASCADE, related_name='bookings')
    status = models.CharField(max_length=10, default='booked', choices=[('booked', 'Booked'), ('waitlist', 'Waitlist'), ('cancelled', 'Cancelled'), ('attended', 'Attended')])
    created = models.DateTimeField(auto_now_add=True)
    class Meta: unique_together = ('user', 'gym_class'); ordering = ['created']

class TrainerSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name='sessions')
    start = models.DateTimeField()
    status = models.CharField(max_length=10, default='booked', choices=[('booked', 'Booked'), ('cancelled', 'Cancelled'), ('completed', 'Completed')])
    class Meta:
        ordering = ['start']
        constraints = [models.UniqueConstraint(fields=['trainer', 'start'], condition=~Q(status='cancelled'), name='no_double_booking')]

class Lead(models.Model):
    STATUS = [(s, s.replace('_', ' ').title()) for s in ('new', 'contacted', 'trial_booked', 'trial_completed', 'converted', 'not_interested')]
    name = models.CharField(max_length=80); email = models.EmailField(); phone = models.CharField(max_length=30)
    age = models.PositiveIntegerField(null=True, blank=True); goal = models.CharField(max_length=80, blank=True)
    preferred_date = models.DateField(null=True, blank=True); preferred_time = models.CharField(max_length=20, blank=True)
    level = models.CharField(max_length=20, blank=True); status = models.CharField(max_length=20, choices=STATUS, default='new')
    created = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['-created']

class TourRequest(models.Model):
    name = models.CharField(max_length=80); email = models.EmailField(); phone = models.CharField(max_length=30)
    date = models.DateField(); time = models.TimeField()
    status = models.CharField(max_length=12, default='pending', choices=[(s, s.title()) for s in ('pending', 'approved', 'rescheduled', 'cancelled', 'completed')])
    created = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['-created']

class ContactMessage(models.Model):
    name = models.CharField(max_length=80); email = models.EmailField(); phone = models.CharField(max_length=30, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=10, default='new', choices=[(s, s.title()) for s in ('new', 'read', 'responded', 'closed')])
    created = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['-created']

class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance')
    check_in = models.DateTimeField(default=timezone.now); check_out = models.DateTimeField(null=True, blank=True)
    class Meta: ordering = ['-check_in']

class Testimonial(models.Model):
    name = models.CharField(max_length=80); quote = models.TextField(); rating = models.PositiveIntegerField(default=5)
    photo = models.ImageField(upload_to='testimonials/', blank=True); published = models.BooleanField(default=False)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=240); read = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['-created']
