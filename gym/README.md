# Form & Flow — one project, frontend + backend (Django)

This is the WHOLE site: the marketing pages, the member/trainer/admin backend, and the database, all in one
Django project. There's no separate 'frontend folder' anymore — the same design now IS the live site, rendered
from real data (classes, plans, testimonials, etc.) instead of the earlier standalone mockup.

static/css/style.css and static/js/site.js  -> the design + page chrome (menu, parallax, WhatsApp bubble)
core/templates/core/*.html                  -> every page (home, classes, plans, dashboard, admin views...)
core/{models,views,forms,services}.py       -> the backend logic


## Run locally (Windows / VS Code terminal)
```
py -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
py manage.py migrate
py manage.py seed            # DEMO data only
py manage.py runserver
```
Open http://127.0.0.1:8000  — admin login `admin / admin12345` (demo), members `member1..10 / member12345`.
Staff dashboard: /manage/   Check-in desk: /checkin/   Full admin (plans, classes, trainers, testimonials, payments): /admin/
Tests: `py manage.py test`

## Deploy on PythonAnywhere
1. Upload/clone the project, create a virtualenv (Python 3.10+), `pip install -r requirements.txt`.
2. Create `.env` from `.env.example`: set a long random SECRET_KEY, `DEBUG=False`, ALLOWED_HOSTS=yourname.pythonanywhere.com, SMTP email settings.
3. Put your real WhatsApp number in .env as WHATSAPP_NUMBER (it drives the floating button everywhere). Run `python manage.py migrate` then `python manage.py createsuperuser` (do NOT run `seed` in production).
4. Web tab: WSGI file -> `config.wsgi`; static files: `/static/` -> `<project>/staticfiles`, `/media/` -> `<project>/media`; run `python manage.py collectstatic`.
5. Tasks tab: schedule daily `python manage.py send_reminders` (expiry + class reminders).

## How the business flow works
- Visitor: home -> free trial / tour / contact forms (saved as leads; spam-protected with honeypot + rate limit; admin + visitor emailed).
- Sign up -> verification email -> choose plan -> creates a PENDING payment with a transaction ID -> staff confirms payment
  (/manage/ or Django admin action) -> membership becomes ACTIVE. No card data is ever stored.
- Classes: booking needs an active membership; capacity enforced under a row lock; duplicates blocked; full class => waitlist;
  cancelling auto-promotes the next person and notifies them.
- Trainers: pick a day, see free slots; a database constraint prevents double booking.
- Attendance: each member has a QR/member ID; staff scan at /checkin/ (second scan = check-out; duplicate scans ignored).
- Roles: member / trainer / admin. /manage and /checkin need trainer or admin; everything private needs login.

## Not built yet (next rounds)
Online card payments (Stripe/JazzCash), Google login, fitness-progress charts, admin revenue/attendance charts, CMS for hero/FAQs/facilities,
waitlist "claim" window, SMS/WhatsApp notifications, trainer availability editor, analytics events, full REST API.
