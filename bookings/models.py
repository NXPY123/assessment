# bookings/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.conf import settings

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    # Add unique related_name arguments to avoid clashes
    groups = models.ManyToManyField(
        Group,
        verbose_name=('groups'),
        blank=True,
        help_text=(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="customuser_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=('user permissions'),
        blank=True,
        help_text=('Specific permissions for this user.'),
        related_name="customuser_set",
        related_query_name="user",
    )

    def is_admin(self):
        return self.role == 'admin'

class Station(models.Model):
    name = models.CharField(max_length=100, unique=True, primary_key=True)

    def __str__(self):
        return self.name

class Train(models.Model):
    no = models.CharField(max_length=20, primary_key=True)
    name = models.CharField(max_length=255)
    source = models.ForeignKey(Station, on_delete=models.PROTECT, related_name='trains_from_source')
    destination = models.ForeignKey(Station, on_delete=models.PROTECT, related_name='trains_to_destination')

    def __str__(self):
        return f"Train {self.no}: {self.name}"

class Trip(models.Model):
    id = models.AutoField(primary_key=True)
    train = models.ForeignKey(Train, on_delete=models.CASCADE)
    starting_time_date = models.DateTimeField()
    ending_time_date = models.DateTimeField()
    total_seats = models.IntegerField()
    free_seats = models.IntegerField()

    class Meta:
        unique_together = (('train', 'starting_time_date'), ('train', 'ending_time_date'))

    def __str__(self):
        return f"Trip {self.id} for Train {self.train.no}"

class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    booking_timestamp = models.DateTimeField(auto_now_add=True)
    seat_count = models.IntegerField()

    class Meta:
        unique_together = (('user', 'trip')) # A user can only have one booking per trip

    def __str__(self):
        return f"Booking {self.id} by {self.user.username} for Trip {self.trip.id}"