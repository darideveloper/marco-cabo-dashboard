from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend

from travels import models
from travels import serializers


class ZoneViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Zone.objects.all()
    serializer_class = serializers.ZoneSerializer


class VehicleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Vehicle.objects.all()
    serializer_class = serializers.VehicleSerializer


class TransferTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.TransferType.objects.all()
    serializer_class = serializers.TransferTypeSerializer


class PricingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Pricing.objects.all()
    serializer_class = serializers.PricingSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['location', 'vehicle', 'transfer_type']
