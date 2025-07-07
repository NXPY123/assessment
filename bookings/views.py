# bookings/views.py
from rest_framework import generics, viewsets, status
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import F
from django.shortcuts import get_object_or_404

from .models import CustomUser, Station, Train, Trip, Booking
from .serializers import (
    CustomUserSerializer, StationSerializer, TrainSerializer,
    TripSerializer, BookingSerializer, BookSeatSerializer
)
from .permissions import IsAdminUser, IsBookingOwner

class RegisterUserView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        headers = self.get_success_headers(serializer.data)
        return Response({'username': user.username, 'role': user.role, 'token': token.key}, status=status.HTTP_201_CREATED, headers=headers)

class LoginUserView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'username': user.username,
            'role': user.role
        })

class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    permission_classes = [IsAdminUser] # Only admin can add/modify stations

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            self.permission_classes = [IsAuthenticated] # Anyone can view stations
        return super().get_permissions()


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.all()
    serializer_class = TrainSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['source__name', 'destination__name']
    search_fields = ['name', 'no']
    ordering_fields = ['name', 'no']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAdminUser]
        elif self.action in ['list', 'retrieve']:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAdminUser]
        elif self.action in ['list', 'retrieve']:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()


class AvailabilityView(generics.ListAPIView):
    serializer_class = TripSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'train__source__name': ['exact'],
        'train__destination__name': ['exact'],
        'starting_time_date': ['date__exact', 'date__gte', 'date__lte'] # Filter by date
    }

    def get_queryset(self):
        queryset = Trip.objects.all().annotate(
            available_seats=F('free_seats')
        )
        return queryset

class BookSeatView(generics.CreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookSeatSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # The atomic transaction and seat update are handled in the serializer's create method
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        try:
            serializer.is_valid(raise_exception=True)
            booking = self.perform_create(serializer)
            return Response({'message': 'Seats booked successfully!', 'booking_id': booking.id, 'trip_id': booking.trip.id, 'seat_count': booking.seat_count}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class GetUserBookingsView(generics.ListAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        trip_id = self.kwargs.get('trip_id')
        if trip_id:
            return Booking.objects.filter(user=user, trip__id=trip_id)
        return Booking.objects.filter(user=user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists() and self.kwargs.get('trip_id'):
            return Response({'detail': 'No booking found for this trip and user.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)