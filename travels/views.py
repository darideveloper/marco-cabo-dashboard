from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
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


class VipCodeValidationView(APIView):
    """
    API endpoint to validate VIP codes
    """
    
    def post(self, request):
        serializer = serializers.VipCodeValidationSerializer(data=request.data)
        
        if serializer.is_valid():
            return Response({
                "status": "sucess",
                "message": "VIP code is valid",
                "data": []
            })
        else:
            return Response({
                "status": "error",
                "message": "Invalid VIP code",
                "data": [],
            }, status=status.HTTP_400_BAD_REQUEST)
