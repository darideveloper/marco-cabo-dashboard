from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# from rest_framework.permissions import AllowAny

from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings

from travels import models
from travels import serializers
from utils.stripe import get_payment_link


class ZoneViewSet(viewsets.ReadOnlyModelViewSet):
    # Return all zones except "Postal Code"
    queryset = models.Zone.objects.exclude(name="Codigo Postal").order_by("id")
    serializer_class = serializers.ZoneSerializer


class VehicleViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Vehicle.objects.all().order_by("id")
    serializer_class = serializers.VehicleSerializer


class ServiceTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.ServiceType.objects.all().order_by("id")
    serializer_class = serializers.ServiceTypeSerializer


class PricingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Pricing.objects.all().order_by("id")
    serializer_class = serializers.PricingSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["location", "vehicle", "service_type"]


class VipCodeValidationView(APIView):
    """
    API endpoint to validate VIP codes
    """

    def post(self, request):
        serializer = serializers.VipCodeValidationSerializer(data=request.data)

        if serializer.is_valid():
            return Response(
                {"status": "sucess", "message": "VIP code is valid", "data": []}
            )
        else:
            return Response(
                {
                    "status": "error",
                    "message": "Invalid VIP code",
                    "data": [],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class SaleViewSet(APIView):
    """
    API endpoint to create sales
    """

    def post(self, request):
        serializer = serializers.SaleSerializer(data=request.data)

        if serializer.is_valid():
            # Create data
            sale = serializer.save()

            # Go directly to confirmation page if vip code
            # Or generate payment
            payment_link = settings.LANDING_HOST_SUCCESS
            if not sale.vip_code:
                payment_link = get_payment_link(
                    product_name="Marco Cabo Transfer",
                    total=sale.total,
                    description=sale.get_summary(),
                    email=sale.client.email,
                    sale_id=sale.stripe_code,
                )

            return Response(
                {
                    "status": "success",
                    "message": "Sale created successfully",
                    "data": {"sale_id": sale.id, "payment_link": payment_link},
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {
                    "status": "error",
                    "message": "Invalid sale data",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class SaleDoneView(APIView):
    """
    API endpoint to confirm a sale
    """

    # permission_classes = [AllowAny]

    def post(self, request):
        serializer = serializers.SaleDoneSerializer(data=request.data)

        if serializer.is_valid():
            try:
                sale = models.Sale.objects.filter(
                    stripe_code=serializer.validated_data["sale_stripe_code"]
                ).first()
            except Exception:
                return Response(
                    {
                        "status": "error",
                        "message": "Invalid sale data",
                        "data": serializer.errors,
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # Update client
            client = sale.client
            client.last_name = serializer.validated_data["client"]["last_name"]
            client.phone = serializer.validated_data["client"]["phone"]
            client.save()

            # Confirm sale
            sale.paid = True
            sale.save()
            models.Transfer.objects.create(
                sale=sale,
                type="arrival",
                date=serializer.validated_data["arrival"]["date"],
                hour=serializer.validated_data["arrival"]["hour"],
                airline=serializer.validated_data["arrival"]["airline"],
                flight_number=serializer.validated_data["arrival"]["flight_number"],
            )
            if sale.service_type.name == "Round Trip":
                models.Transfer.objects.create(
                    sale=sale,
                    type="departure",
                    date=serializer.validated_data["departure"]["date"],
                    hour=serializer.validated_data["departure"]["hour"],
                    airline=serializer.validated_data["departure"]["airline"],
                    flight_number=serializer.validated_data["departure"]["flight_number"],
                )

            # Check if sale is already confirmed
            return Response(
                {
                    "status": "success",
                    "message": "Sale confirmed successfully",
                    "data": [],
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    "status": "error",
                    "message": "Invalid sale data",
                    "data": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
