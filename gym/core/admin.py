from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from . import models as m

@admin.register(m.User)
class U(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (('Gym', {'fields': ('role', 'phone', 'photo', 'email_verified', 'member_code')}),)
    list_display = ('username', 'email', 'role', 'is_active'); list_filter = ('role', 'is_active'); search_fields = ('username', 'email', 'member_code')
@admin.register(m.Payment)
class P(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'amount', 'status', 'provider', 'created'); list_filter = ('status', 'provider')
    actions = ['mark_paid']
    @admin.action(description='Mark selected payments as PAID and activate their memberships')
    def mark_paid(self, request, qs):
        from .services import activate_membership
        for p in qs.filter(status='pending'):
            p.status = 'paid'; p.save()
            if p.membership: activate_membership(p.membership)
@admin.register(m.GymClass)
class C(admin.ModelAdmin): list_display = ('name', 'start', 'trainer', 'capacity', 'active'); list_filter = ('name', 'trainer', 'active')
@admin.register(m.Lead)
class L(admin.ModelAdmin): list_display = ('name', 'email', 'phone', 'status', 'created'); list_filter = ('status',); list_editable = ('status',)
@admin.register(m.TourRequest)
class T(admin.ModelAdmin): list_display = ('name', 'date', 'time', 'status'); list_filter = ('status',); list_editable = ('status',)
@admin.register(m.ContactMessage)
class CM(admin.ModelAdmin): list_display = ('name', 'email', 'status', 'created'); list_filter = ('status',); list_editable = ('status',)
@admin.register(m.Testimonial)
class TE(admin.ModelAdmin): list_display = ('name', 'rating', 'published'); list_editable = ('published',)
for model in (m.Plan, m.Membership, m.Trainer, m.Booking, m.TrainerSession, m.Attendance, m.Notification): admin.site.register(model)
