# bookings/serializers.py
from rest_framework import serializers
from .models import CustomUser, Station, Train, Trip, Booking
from django.contrib.auth.hashers import make_password
from django.db import transaction

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('username', 'password', 'role')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data.get('password'))
        user = CustomUser.objects.create(**validated_data)
        return user

class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = '__all__'

class TrainSerializer(serializers.ModelSerializer):
    source = serializers.SlugRelatedField(queryset=Station.objects.all(), slug_field='name')
    destination = serializers.SlugRelatedField(queryset=Station.objects.all(), slug_field='name')

    class Meta:
        model = Train
        fields = '__all__'

class TripSerializer(serializers.ModelSerializer):
    train = serializers.SlugRelatedField(queryset=Train.objects.all(), slug_field='no')

    class Meta:
        model = Trip
        fields = '__all__'
        read_only_fields = ('free_seats',) # free_seats will be managed by the system

class BookingSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username') # Display username, not user ID
    trip = serializers.SlugRelatedField(queryset=Trip.objects.all(), slug_field='id')

    class Meta:
        model = Booking
        fields = '__all__'
        read_only_fields = ('booking_timestamp',)

class BookSeatSerializer(serializers.Serializer):
    trip_id = serializers.PrimaryKeyRelatedField(queryset=Trip.objects.all())
    seat_count = serializers.IntegerField(min_value=1)

    def validate(self, data):
        trip = data['trip_id']
        seat_count = data['seat_count']

        if trip.free_seats < seat_count:
            raise serializers.ValidationError("Not enough seats available.")
        return data

    def create(self, validated_data):
        trip = validated_data['trip_id']
        seat_count = validated_data['seat_count']
        user = self.context['request'].user

        with transaction.atomic():
            # Lock the trip row to prevent race conditions
            trip_for_update = Trip.objects.select_for_update().get(pk=trip.pk)

            if trip_for_update.free_seats < seat_count:
                raise serializers.ValidationError("Not enough seats available (race condition).")

            trip_for_update.free_seats -= seat_count
            trip_for_update.save()

            # Check if a booking already exists for this user and trip
            booking, created = Booking.objects.get_or_create(
                user=user,
                trip=trip_for_update,
                defaults={'seat_count': seat_count}
            )
            if not created:
                # If booking already exists, update seat count
                booking.seat_count += seat_count
                booking.save()

            return booking