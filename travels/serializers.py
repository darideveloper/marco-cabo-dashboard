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
    service_type = ServiceTypeSerializer(read_only=True)

    class Meta:
        model = models.Pricing
        fields = (
            "id",
            "location",
            "vehicle",
            "service_type",
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
        queryset=models.ServiceType.objects.all()
    )
    client_name = serializers.CharField(source="client.name")
    client_last_name = serializers.CharField(source="client.last_name")
    client_email = serializers.EmailField(source="client.email")
    client_phone = serializers.CharField(source="client.phone")
    passengers = serializers.IntegerField()
    location = serializers.PrimaryKeyRelatedField(
        queryset=models.Location.objects.all()
    )
    vip_code = serializers.SlugRelatedField(
        queryset=models.VipCode.objects.filter(active=True),
        slug_field="value",
        required=False,
        allow_null=True,
    )
    arrival_date = serializers.DateField(source="arrival.date")
    arrival_time = serializers.TimeField(source="arrival.hour")
    arrival_airline = serializers.CharField(source="arrival.airline")
    arrival_flight_number = serializers.CharField(source="arrival.flight_number")
    departure_date = serializers.DateField(source="departure.date", required=False)
    departure_time = serializers.TimeField(source="departure.hour", required=False)
    departure_airline = serializers.CharField(
        source="departure.airline", required=False
    )
    departure_flight_number = serializers.CharField(
        source="departure.flight_number", required=False
    )
    vehicle = serializers.PrimaryKeyRelatedField(queryset=models.Vehicle.objects.all())

    def create(self, validated_data):

        # Create client
        client = models.Client.objects.create(**validated_data["client"])
        
        # Get total from pricing
        pricing = models.Pricing.objects.get(
            location=validated_data["location"],
            vehicle=validated_data["vehicle"],
            service_type=validated_data["service_type"],
        )
        
        # Create sale
        sale_data = {
            "client": client,
            "vip_code": validated_data.get("vip_code", None),
            "vehicle": validated_data["vehicle"],
            "service_type": validated_data["service_type"],
            "location": validated_data["location"],
            "passengers": validated_data["passengers"],
            "total": pricing.price,
        }
        sale = models.Sale.objects.create(**sale_data)

        # Create transfers
        models.Transfer.objects.create(
            **validated_data["arrival"],
            type="arrival",
            sale=sale,
        )
        if "departure" in validated_data:
            models.Transfer.objects.create(
                **validated_data["departure"],
                type="departure",
                sale=sale,
            )

        return sale