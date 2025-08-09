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


class ServiceTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.ServiceType.objects.all()
    serializer_class = serializers.ServiceTypeSerializer


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


class SaleViewSet(APIView):
    """
    API endpoint to create sales
    """

    def post(self, request):
        serializer = serializers.SaleSerializer(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data

            # Obtener datos del cliente o crearlo
            client, _ = models.Client.objects.get_or_create(
                name=data["client"]["name"],
                last_name=data["client"]["last_name"],
                email=data["client"]["email"],
                phone=data["client"]["phone"]
            )

            # Obtener vehículo, VIP y ubicación
            vehicle = models.Vehicle.objects.get(id=data["vehicle"]["id"])
            vip_code = models.VipCode.objects.get(value=data["vip_code"])
            location = models.Location.objects.get(id=data["location"]["id"])

            # Determinar tipo de servicio según departure
            has_departure = (
                data.get("departure", {}).get("date") and
                data.get("departure", {}).get("hour")
            )
            if has_departure:
                service_type = models.ServiceType.objects.get(name__iexact="Round Trip")
            else:
                service_type = models.ServiceType.objects.get(name__iexact="One Way")

            # Crear la venta
            sale = models.Sale.objects.create(
                client=client,
                vip_code=vip_code,
                vehicle=vehicle,
                passengers=data["passengers"],
                service_type=service_type
            )

            # Crear transfer de llegada
            arrival_data = data.get("arrival", {})
            models.Transfer.objects.create(
                date=arrival_data["date"],
                hour=arrival_data["hour"],
                location=location,
                type="Arrival",
                sale=sale,
                airline=arrival_data["airline"],
                flight_number=arrival_data["flight_number"]
            )

            # Crear transfer de salida (solo si hay datos)
            if has_departure:
                departure_data = data.get("departure", {})
                models.Transfer.objects.create(
                    date=departure_data["date"],
                    hour=departure_data["hour"],
                    location=location,
                    type="Departure",
                    sale=sale,
                    airline=departure_data["airline"],
                    flight_number=departure_data["flight_number"]
                )

            return Response({
                "status": "success",
                "message": "Sale created successfully",
                "data": {"sale_id": sale.id}
            }, status=status.HTTP_201_CREATED)

        return Response({
            "status": "error",
            "message": "Invalid sale data",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)