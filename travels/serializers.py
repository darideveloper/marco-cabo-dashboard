from rest_framework import serializers

from travels import models


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Location
        fields = ("id", "name")


class ZoneSerializer(serializers.ModelSerializer):
    locations = LocationSerializer(many=True, read_only=True)

    class Meta:
        model = models.Zone
        fields = ("id", "name", "locations")


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Vehicle
        fields = ("id", "name")


class ServiceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ServiceType
        fields = ("id", "name")


class PricingSerializer(serializers.ModelSerializer):
    location = LocationSerializer(read_only=True)
    vehicle = VehicleSerializer(read_only=True)
    transfer_type = ServiceTypeSerializer(read_only=True)

    class Meta:
        model = models.Pricing
        fields = (
            "id",
            "location",
            "vehicle",
            "transfer_type",
            "price",
        )


class VipCodeValidationSerializer(serializers.Serializer):
    vip_code = serializers.CharField(max_length=10, required=True)
    
    def validate_vip_code(self, value):
        """
        Validate that the VIP code exists and is active
        """
        try:
            models.VipCode.objects.get(value=value, active=True)
            return value
        except models.VipCode.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive VIP code")


class SaleSerializer(serializers.Serializer):
    service_type = serializers.IntegerField(source="service_type.id", required=True)
    client_name = serializers.CharField(source="client.name", required=True)
    client_last_name = serializers.CharField(source="client.last_name", required=True)
    passengers = serializers.IntegerField(required=True)
    client_email = serializers.EmailField(source="client.email", required=True)
    client_phone = serializers.CharField(source="client.phone", required=True)
    location = serializers.IntegerField(source="location.id", required=True)
    vip_code = serializers.CharField(max_length=10, required=True)
    arrival_date = serializers.DateField(source="arrival.date")
    arrival_time = serializers.TimeField(source="arrival.hour")
    arrival_airline = serializers.CharField(source="arrival.airline")
    arrival_flight_number = serializers.CharField(source="arrival.flight_number")
    departure_date = serializers.DateField(source="departure.date")
    departure_time = serializers.TimeField(source="departure.hour")
    departure_airline = serializers.CharField(source="departure.airline")
    departure_flight_number = serializers.CharField(source="departure.flight_number")
    vehicle = serializers.IntegerField(source="vehicle.id")

    def validate_vip_code(self, value):
        """
        Validate that the VIP code exists and is active
        """
        try:
            models.VipCode.objects.get(value=value, active=True)
            return value
        except models.VipCode.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive VIP code")