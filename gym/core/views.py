import io
from datetime import timedelta
from django.contrib import messages
from django.contrib.auth import login, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.tokens import default_token_generator
from django.core import signing
from django.core.cache import cache
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.conf import settings
from django.db import transaction
from django.db.models import Sum, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST
from . import forms as f, models as m, services as s

staff_only = user_passes_test(lambda u: u.is_authenticated and (u.is_gym_admin or u.role == 'trainer'), login_url='/login/')

def throttle(request, key, limit=5, seconds=3600):
    k = f"th:{key}:{request.META.get('REMOTE_ADDR')}"
    n = cache.get(k, 0)
    if n >= limit: return True
    cache.set(k, n + 1, seconds); return False

def home(request):
    return render(request, 'core/home.html', {
        'plans': m.Plan.objects.filter(active=True), 'trainers': m.Trainer.objects.filter(active=True),
        'classes': m.GymClass.objects.filter(active=True, start__gte=timezone.now())[:6],
        'testimonials': m.Testimonial.objects.filter(published=True),
        'member_count': m.Membership.objects.filter(status='active', end__gte=timezone.localdate()).values('user').distinct().count()})

def classes(request):
    qs = m.GymClass.objects.filter(active=True, start__gte=timezone.now())
    if request.GET.get('type'): qs = qs.filter(name__icontains=request.GET['type'])
    return render(request, 'core/classes.html', {'classes': qs, 'types': ['Pilates', 'Yoga', 'Strength', 'Mobility', 'HIIT']})

def api_availability(request, pk):
    gc = get_object_or_404(m.GymClass, pk=pk)
    return JsonResponse({'capacity': gc.capacity, 'booked': gc.booked, 'spots_left': gc.spots_left, 'full': gc.is_full})

def api_plans(request):
    return JsonResponse({'plans': [{'id': p.id, 'name': p.name, 'monthly': str(p.price_monthly), 'yearly': str(p.price_yearly)} for p in m.Plan.objects.filter(active=True)]})

# ---------- auth ----------
def _verify_link(request, user):
    token = signing.dumps(user.pk, salt='verify')
    send_mail('Verify your email', f'Welcome to Form & Flow! Verify: {request.build_absolute_uri("/verify/" + token + "/")}', settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=True)

def signup(request):
    form = f.SignupForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(); login(request, user); _verify_link(request, user)
        s.notify(user, 'Welcome to Form & Flow! Check your inbox to verify your email.', email=False)
        messages.success(request, 'Account created. Please verify your email.'); return redirect('dashboard')
    return render(request, 'core/form.html', {'form': form, 'title': 'Create your account', 'button': 'Sign up'})

def verify(request, token):
    try: pk = signing.loads(token, salt='verify', max_age=86400 * 3)
    except signing.BadSignature:
        messages.error(request, 'That verification link is invalid or expired.'); return redirect('home')
    get_user_model().objects.filter(pk=pk).update(email_verified=True)
    messages.success(request, 'Email verified. Thank you!'); return redirect('dashboard')

@login_required
def profile(request):
    form = f.ProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save(); messages.success(request, 'Profile updated.'); return redirect('dashboard')
    return render(request, 'core/form.html', {'form': form, 'title': 'Your profile', 'button': 'Save', 'multipart': True})

# ---------- member ----------
@login_required
def dashboard(request):
    u = request.user; now = timezone.now()
    return render(request, 'core/dashboard.html', {
        'membership': u.active_membership,
        'upcoming': u.bookings.filter(status__in=['booked', 'waitlist'], gym_class__start__gte=now).select_related('gym_class__trainer'),
        'sessions': u.sessions.filter(status='booked', start__gte=now).select_related('trainer'),
        'payments': u.payments.all()[:5], 'attendance': u.attendance.all()[:5],
        'streak': _streak(u), 'notes': u.notifications.all()[:5], 'total_visits': u.attendance.count()})

def _streak(u):
    days = sorted({a.check_in.date() for a in u.attendance.all()}, reverse=True); n = 0; d = timezone.localdate()
    if days and days[0] == d - timedelta(days=1): d = d - timedelta(days=1)
    for x in days:
        if x == d: n += 1; d -= timedelta(days=1)
        elif x < d: break
    return n

@login_required
def plans(request):
    return render(request, 'core/plans.html', {'plans': m.Plan.objects.filter(active=True), 'current': request.user.active_membership})

@login_required
@require_POST
def buy_plan(request, pk):
    plan = get_object_or_404(m.Plan, pk=pk, active=True); cycle = request.POST.get('cycle', 'monthly')
    if cycle not in ('monthly', 'yearly'): cycle = 'monthly'
    cur = request.user.active_membership; start = timezone.localdate()
    if cur and cur.plan_id == plan.pk: start = cur.end  # renewal extends
    end = start + timedelta(days=365 if cycle == 'yearly' else 30)
    ms = m.Membership.objects.create(user=request.user, plan=plan, cycle=cycle, start=start, end=end)
    amount = plan.price_yearly if cycle == 'yearly' else plan.price_monthly
    p = m.Payment.objects.create(user=request.user, membership=ms, amount=amount)
    messages.success(request, f'Order {p.transaction_id} created. Pay at the front desk or by bank transfer using this reference — your membership activates when we confirm payment.')
    return redirect('dashboard')

@login_required
@require_POST
def book(request, pk):
    _, msg = s.book_class(request.user, pk); messages.info(request, msg); return redirect(request.POST.get('next') or 'classes')

@login_required
@require_POST
def cancel(request, pk):
    messages.info(request, s.cancel_booking(request.user, pk)); return redirect('dashboard')

@login_required
def trainers(request):
    return render(request, 'core/trainers.html', {'trainers': m.Trainer.objects.filter(active=True)})

@login_required
def book_trainer(request, pk):
    t = get_object_or_404(m.Trainer, pk=pk, active=True)
    date = request.GET.get('date') or str(timezone.localdate() + timedelta(days=1)); slots = []
    try:
        day = timezone.datetime.fromisoformat(date).date()
        taken = set(t.sessions.exclude(status='cancelled').filter(start__date=day).values_list('start', flat=True))
        for h in range(7, 20):
            st = timezone.make_aware(timezone.datetime.combine(day, timezone.datetime.min.time().replace(hour=h)))
            if st > timezone.now(): slots.append((st, st in taken))
    except ValueError: messages.error(request, 'Invalid date.')
    if request.method == 'POST':
        try:
            st = timezone.datetime.fromisoformat(request.POST['slot'])
            st = st if timezone.is_aware(st) else timezone.make_aware(st)
            if st <= timezone.now(): raise ValueError
            with transaction.atomic(): m.TrainerSession.objects.create(user=request.user, trainer=t, start=st)
            s.notify(request.user, f'Session booked with {t.name} on {st:%a %d %b at %H:%M}.')
            messages.success(request, 'Your session has been booked successfully.')
        except Exception: messages.error(request, 'That time slot is no longer available.')
        return redirect('dashboard')
    return render(request, 'core/book_trainer.html', {'trainer': t, 'slots': slots, 'date': date})

@login_required
def qr(request):
    import qrcode
    buf = io.BytesIO(); qrcode.make(request.user.member_code).save(buf, format='PNG')
    return HttpResponse(buf.getvalue(), content_type='image/png')

# ---------- public lead forms ----------
def _public_form(request, Form, title, done_msg, notify_subject):
    form = Form(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        if throttle(request, Form.__name__):
            messages.error(request, 'Too many submissions — please try again later.')
        else:
            obj = form.save(); messages.success(request, done_msg)
            send_mail(notify_subject, str(form.cleaned_data), settings.DEFAULT_FROM_EMAIL, [a[1] for a in settings.ADMINS] or [settings.DEFAULT_FROM_EMAIL], fail_silently=True)
            if getattr(obj, 'email', None): send_mail('Form & Flow — we got your request', done_msg, settings.DEFAULT_FROM_EMAIL, [obj.email], fail_silently=True)
            return redirect('home')
    return render(request, 'core/form.html', {'form': form, 'title': title, 'button': 'Send'})

def trial(request): return _public_form(request, f.LeadForm, 'Start your free trial', 'Thanks — your free trial request is in. We will contact you shortly.', 'New free-trial lead')
def tour(request): return _public_form(request, f.TourForm, 'Book a gym tour', 'Your tour request has been received. We will confirm it shortly.', 'New tour request')
def contact(request): return _public_form(request, f.ContactForm, 'Contact us', 'Thanks for your message — we will reply soon.', 'New contact message')

def quiz(request):
    form = f.QuizForm(request.POST or None); rec = None
    if request.method == 'POST' and form.is_valid():
        d = form.cleaned_data; plans = list(m.Plan.objects.filter(active=True).order_by('price_monthly'))
        pick = plans[-1] if d['level'] == 'advanced' or d['days'] >= 5 else (plans[len(plans) // 2] if d['days'] >= 3 else plans[0]) if plans else None
        cls = {'muscle': 'Strength', 'weight': 'HIIT', 'strength': 'Strength', 'endurance': 'HIIT', 'mobility': 'Mobility', 'general': 'Pilates'}[d['goal']]
        rec = {'plan': pick, 'class': cls, 'trainer': m.Trainer.objects.filter(active=True, specialization__icontains=cls).first() or m.Trainer.objects.filter(active=True).first()}
    return render(request, 'core/form.html', {'form': form, 'title': 'Find your program', 'button': 'Recommend', 'rec': rec})

# ---------- staff ----------
@staff_only
def checkin(request):
    if request.method == 'POST':
        code = request.POST.get('code', '').strip().upper()
        u = m.User.objects.filter(member_code=code).first()
        if not u: messages.error(request, 'Unknown member code.')
        else:
            last = u.attendance.first()
            if last and last.check_out is None and timezone.now() - last.check_in < timedelta(hours=6):
                last.check_out = timezone.now(); last.save(); messages.success(request, f'{u.get_full_name() or u.username} checked OUT.')
            elif last and timezone.now() - last.check_in < timedelta(minutes=5): messages.warning(request, 'Duplicate scan ignored.')
            elif not u.active_membership: messages.error(request, f'{u.username}: no active membership.')
            else: m.Attendance.objects.create(user=u); messages.success(request, f'{u.get_full_name() or u.username} checked IN.')
    return render(request, 'core/checkin.html', {'today': m.Attendance.objects.filter(check_in__date=timezone.localdate()).select_related('user')})

@staff_only
def manage(request):
    today = timezone.localdate(); U = m.User.objects.filter(role='member')
    stats = [('Total members', U.count()), ('Active memberships', m.Membership.objects.filter(status='active', end__gte=today).values('user').distinct().count()),
             ('New this month', U.filter(date_joined__month=today.month, date_joined__year=today.year).count()),
             ("Today's check-ins", m.Attendance.objects.filter(check_in__date=today).count()),
             ("Today's class bookings", m.Booking.objects.filter(gym_class__start__date=today, status='booked').count()),
             ('Revenue this month', '$%s' % (m.Payment.objects.filter(status='paid', created__month=today.month, created__year=today.year).aggregate(t=Sum('amount'))['t'] or 0)),
             ('Pending payments', m.Payment.objects.filter(status='pending').count()), ('New trial leads', m.Lead.objects.filter(status='new').count()),
             ('Tour requests', m.TourRequest.objects.filter(status='pending').count()), ('Unread messages', m.ContactMessage.objects.filter(status='new').count())]
    q = request.GET.get('q', ''); members = U.filter(Q(username__icontains=q) | Q(email__icontains=q) | Q(member_code__icontains=q)) if q else U
    page = Paginator(members.order_by('-date_joined'), 10).get_page(request.GET.get('page'))
    pending = m.Payment.objects.filter(status='pending').select_related('user', 'membership__plan')
    return render(request, 'core/manage.html', {'stats': stats, 'page': page, 'q': q, 'pending': pending, 'leads': m.Lead.objects.all()[:8], 'tours': m.TourRequest.objects.all()[:8]})

@staff_only
@require_POST
def confirm_payment(request, pk):
    p = get_object_or_404(m.Payment, pk=pk, status='pending'); p.status = 'paid'; p.save()
    if p.membership: s.activate_membership(p.membership)
    messages.success(request, f'Payment {p.transaction_id} confirmed.'); return redirect('manage')
