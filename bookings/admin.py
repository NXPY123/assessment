# bookings/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Station, Train, Trip, Booking

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (('Role'), {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (('Role'), {'fields': ('role',)}),
    )

admin.site.register(Station)
admin.site.register(Train)
admin.site.register(Trip)
admin.site.register(Booking)