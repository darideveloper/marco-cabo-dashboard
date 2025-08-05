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


class TransferTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TransferType
        fields = ("id", "name")


class PricingSerializer(serializers.ModelSerializer):
    location = LocationSerializer(read_only=True)
    vehicle = VehicleSerializer(read_only=True)
    transfer_type = TransferTypeSerializer(read_only=True)

    class Meta:
        model = models.Pricing
        fields = (
            "id",
            "location",
            "vehicle",
            "transfer_type",
            "price",
        )
