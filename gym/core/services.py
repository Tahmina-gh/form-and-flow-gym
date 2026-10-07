from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from .models import Booking, GymClass, Notification

def notify(user, message, email=True):
    Notification.objects.create(user=user, message=message)
    if email and user.email:
        send_mail('Form & Flow', message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=True)

@transaction.atomic
def book_class(user, class_id):
    """Race-safe booking: locks the class row, prevents duplicates, falls back to waitlist."""
    gc = GymClass.objects.select_for_update().get(pk=class_id, active=True)
    if gc.start < timezone.now(): return None, 'That class has already started.'
    m = user.active_membership
    if not m: return None, 'You need an active membership to book classes.'
    has_room = gc.spots_left > 0  # computed BEFORE we add this user
    b = Booking.objects.filter(user=user, gym_class=gc).first()
    if b and b.status in ('booked', 'waitlist'): return b, 'You are already on this class.'
    if not b: b = Booking(user=user, gym_class=gc)
    b.status = 'booked' if has_room else 'waitlist'
    b.save()
    if b.status == 'booked':
        notify(user, f'Booked: {gc.name} on {gc.start:%a %d %b at %H:%M}.')
        return b, 'Your class has been booked successfully.'
    return b, 'This class is full — you have joined the waitlist.'

@transaction.atomic
def cancel_booking(user, class_id):
    gc = GymClass.objects.select_for_update().get(pk=class_id)
    b = Booking.objects.filter(user=user, gym_class=gc, status__in=['booked', 'waitlist']).first()
    if not b: return 'No active booking found.'
    was_booked = b.status == 'booked'
    b.status = 'cancelled'; b.save()
    if was_booked:  # promote next person on the waitlist
        nxt = gc.bookings.filter(status='waitlist').order_by('created').first()
        if nxt:
            nxt.status = 'booked'; nxt.save()
            notify(nxt.user, f'A spot opened up — you are now booked into {gc.name} on {gc.start:%a %d %b at %H:%M}.')
    return 'Your booking has been cancelled.'

def activate_membership(membership):
    membership.status = 'active'; membership.save()
    notify(membership.user, f'Your {membership.plan.name} membership is active until {membership.end:%d %b %Y}.')
