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
    
    service_type = serializers.PrimaryKeyRelatedField(
        queryset=models.ServiceType.objects.all(), required=True
    )
    client_name = serializers.CharField(required=True)
    client_last_name = serializers.CharField(required=True)
    client_email = serializers.EmailField(required=True)
    client_phone = serializers.CharField(required=True)
    passengers = serializers.IntegerField(required=True)
    location = serializers.PrimaryKeyRelatedField(
        queryset=models.Location.objects.all(), required=True
    )
    vip_code = serializers.SlugRelatedField(
        queryset=models.VipCode.objects.all(),
        slug_field="value",
        required=False,
        allow_null=True,
    )
    arrival_date = serializers.DateField(required=True)
    arrival_time = serializers.TimeField(required=True)
    arrival_airline = serializers.CharField(required=True)
    arrival_flight_number = serializers.CharField(required=True)
    departure_date = serializers.DateField(required=True)
    departure_time = serializers.TimeField(required=True)
    departure_airline = serializers.CharField(required=True)
    departure_flight_number = serializers.CharField(required=True)
    vehicle = serializers.PrimaryKeyRelatedField(
        queryset=models.Vehicle.objects.all(), required=True
    )
    
    class Meta:
        model = models.Sale
        fields = (
            "service_type",
            "client_name",
            "client_last_name",
            "client_email",
            "client_phone",
            "passengers",
            "location",
            "vip_code",
            "arrival_date",
            "arrival_time",
            "arrival_airline",
            "arrival_flight_number",
            "departure_date",
            "departure_time",
            "departure_airline",
            "departure_flight_number",
            "vehicle",
        )

    # def validate_vip_code(self, value):
    #     """
    #     Validate that the VIP code exists and is active
    #     """
    #     try:
    #         models.VipCode.objects.get(value=value, active=True)
    #         return value
    #     except models.VipCode.DoesNotExist:
    #         raise serializers.ValidationError("Invalid or inactive VIP code")
