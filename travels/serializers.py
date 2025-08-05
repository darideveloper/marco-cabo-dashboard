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
        fields = "__all__"
