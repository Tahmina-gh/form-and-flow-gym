from django.contrib.auth import views as a
from django.urls import path
from . import views as v, forms as f

urlpatterns = [
    path('', v.home, name='home'), path('classes/', v.classes, name='classes'),
    path('signup/', v.signup, name='signup'), path('verify/<str:token>/', v.verify),
    path('login/', a.LoginView.as_view(template_name='core/form.html', extra_context={'title': 'Log in', 'button': 'Log in'}), name='login'),
    path('logout/', a.LogoutView.as_view(), name='logout'),
    path('password/change/', a.PasswordChangeView.as_view(template_name='core/form.html', success_url='/dashboard/', extra_context={'title': 'Change password', 'button': 'Change'}), name='password_change'),
    path('password/reset/', a.PasswordResetView.as_view(template_name='core/form.html', success_url='/login/', extra_context={'title': 'Reset password', 'button': 'Email me a link'}), name='password_reset'),
    path('reset/<uidb64>/<token>/', a.PasswordResetConfirmView.as_view(template_name='core/form.html', success_url='/login/', extra_context={'title': 'Choose a new password', 'button': 'Save'}), name='password_reset_confirm'),
    path('profile/', v.profile, name='profile'), path('dashboard/', v.dashboard, name='dashboard'),
    path('membership/', v.plans, name='plans'), path('membership/<int:pk>/buy/', v.buy_plan, name='buy_plan'),
    path('classes/<int:pk>/book/', v.book, name='book'), path('classes/<int:pk>/cancel/', v.cancel, name='cancel'),
    path('trainers/', v.trainers, name='trainers'), path('trainers/<int:pk>/book/', v.book_trainer, name='book_trainer'),
    path('my-qr.png', v.qr, name='qr'),
    path('trial/', v.trial, name='trial'), path('tour/', v.tour, name='tour'), path('contact/', v.contact, name='contact'), path('quiz/', v.quiz, name='quiz'),
    path('checkin/', v.checkin, name='checkin'), path('manage/', v.manage, name='manage'), path('manage/payments/<int:pk>/confirm/', v.confirm_payment, name='confirm_payment'),
    path('api/plans/', v.api_plans), path('api/classes/<int:pk>/availability/', v.api_availability),
]
