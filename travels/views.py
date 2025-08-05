from rest_framework import viewsets

from travels import models
from travels import serializers


class ZoneViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Zone.objects.all()
    serializer_class = serializers.ZoneSerializer


class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Location.objects.all()
    serializer_class = serializers.LocationSerializer


class VehicleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Vehicle.objects.all()
    serializer_class = serializers.VehicleSerializer
