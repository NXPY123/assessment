# train_ticket_booking/urls.py
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from bookings.views import (
    RegisterUserView, LoginUserView, StationViewSet,
    TrainViewSet, TripViewSet, AvailabilityView, BookSeatView,
    GetUserBookingsView
)

router = DefaultRouter()
router.register(r'stations', StationViewSet)
router.register(r'trains', TrainViewSet)
router.register(r'trips', TripViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('', include(router.urls)),
    path('availability/', AvailabilityView.as_view(), name='availability'),
    path('book-seat/', BookSeatView.as_view(), name='book-seat'),
    path('my-bookings/', GetUserBookingsView.as_view(), name='my-bookings-all'),
    path('my-bookings/<int:trip_id>/', GetUserBookingsView.as_view(), name='my-bookings-trip'),
]