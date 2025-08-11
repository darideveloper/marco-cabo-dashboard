from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django_filters.rest_framework import DjangoFilterBackend

from travels import models
from travels import serializers

from django.shortcuts import redirect
from django.conf import settings


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
    filterset_fields = ["location", "vehicle", "transfer_type"]


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

            # Get payment link
            # payment_link = create_stripe_checkout_link(
            #     sale_id=sale.id,
            #     email=sale.client.email,
            #     total=sale.total,
            #     description=f"Venta de {sale.vehicle.name}",
            #     product_name=f"Venta de {sale.vehicle.name}",
            # )

            return Response(
                {
                    "status": "success",
                    "message": "Sale created successfully",
                    "data": {"sale_id": sale.id},
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

    def get(self, request, sale_stripe_code):
        try:
            sale = models.Sale.objects.filter(stripe_code=sale_stripe_code).first()
        except Exception:
            return redirect(settings.LANDING_HOST + "?status=error")

        # Confirm sale
        sale.paid = True
        sale.save()

        # Check if sale is already confirmed
        return redirect(settings.LANDING_HOST + "?status=done")