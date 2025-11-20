from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django_filters.rest_framework import DjangoFilterBackend

from travels import models
from travels import serializers
from utils.stripe import get_payment_link


class HotelsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Zone.objects.exclude(name="Codigo Postal").order_by("id")
    serializer_class = serializers.ZoneSerializer


class PostalCodeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Location.objects.filter(zone__name="Codigo Postal").order_by("id")
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


# class VipCodeValidationView(APIView):
#     """
#     API endpoint to validate VIP codes
#     """

#     def post(self, request):
#         serializer = serializers.VipCodeValidationSerializer(data=request.data)

#         if serializer.is_valid():
#             return Response(
#                 {"status": "sucess", "message": "VIP code is valid", "data": []}
#             )
#         else:
#             return Response(
#                 {
#                     "status": "error",
#                     "message": "Invalid VIP code",
#                     "data": [],
#                 },
#                 status=status.HTTP_400_BAD_REQUEST,
#             )


class SaleViewSet(APIView):
    """
    API endpoint to create sales
    """
    
    def get(self, request):
        """Get already saved sale data"""
        
        try:
            # Get stripe code from query params
            stripe_code = request.query_params.get("stripe_code")
            sale = models.Sale.objects.get(stripe_code=stripe_code)
        except Exception:
            return Response(
                {
                    "status": "error",
                    "message": "Sale not found",
                    "data": {},
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return Response(
            {
                "status": "success",
                "message": "Sale data retrieved successfully",
                "data": {
                    "id": sale.id,
                    "service_type": {
                        "id": sale.service_type.id,
                        "name": sale.service_type.name,
                    },
                    "location": {
                        "id": sale.location.id,
                        "name": sale.location.name,
                    },
                    "vehicle": {
                        "id": sale.vehicle.id,
                        "name": sale.vehicle.name,
                        "passengers": sale.vehicle.passengers,
                    },
                    "total": sale.total,
                    "stripe_code": sale.stripe_code,
                    "client": {
                        "name": sale.client.name,
                        "email": sale.client.email,
                    },
                },
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = serializers.SaleSerializer(data=request.data)

        if serializer.is_valid():
            # Create data
            sale = serializer.save()

            # if not sale.vip_code:
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
                    "data": {"payment_link": payment_link},
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

    def post(self, request):
        """Update sale data and confirm sale"""
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

            # return error if sale already paid (already submited)
            if sale.paid:
                return Response(
                    {
                        "status": "error",
                        "message": "Sale already paid",
                        "data": [],
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Update sale
            sale.passengers = serializer.validated_data["sale"]["passengers"]
            sale.details = serializer.validated_data["sale"].get("details", None)
            sale.save()

            # Update client
            client = sale.client
            client.name = serializer.validated_data["client"]["name"]
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
                    flight_number=serializer.validated_data["departure"][
                        "flight_number"
                    ],
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
