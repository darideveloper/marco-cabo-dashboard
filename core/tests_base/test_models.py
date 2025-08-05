from django.test import TestCase

from travels import models


class TestTravelsModelBase(TestCase):
    """Base class for create travels models"""

    def create_zone(self, name: str = "test zone"):
        """Create a zone

        Args:
            name (str): Name of the zone

        Returns:
            Zone: Zone created
        """
        return models.Zone.objects.create(name=name)

    def create_location(self, name: str = "test location", zone: models.Zone = None):
        """Create a location

        Args:
            name (str): Name of the location
            zone (Zone): Zone of the location

        Returns:
            Location: Location created
        """

        if not zone:
            zone = self.create_zone()

        return models.Location.objects.create(
            name=name,
            zone=zone,
        )

    def create_transfer_type(self, name: str = "test transfer type"):
        """Create a transfer type

        Args:
            name (str): Name of the transfer type

        Returns:
            TransferType: Transfer type created
        """
        return models.TransferType.objects.create(name=name)

    def create_vehicle(self, name: str = "test vehicle"):
        """Create a vehicle

        Args:
            name (str): Name of the vehicle

        Returns:
            Vehicle: Vehicle created
        """
        return models.Vehicle.objects.create(name=name)

    def create_pricing(
        self,
        location: models.Location = None,
        vehicle: models.Vehicle = None,
        transfer_type: models.TransferType = None,
        price: float = 100,
    ):
        """Create a pricing

        Args:
            location (Location): Location of the pricing
            vehicle (Vehicle): Vehicle of the pricing
            transfer_type (TransferType): Transfer type of the pricing
            price (float): Price of the pricing

        Returns:
            Pricing: Pricing created
        """

        if not location:
            location = self.create_location()

        if not vehicle:
            vehicle = self.create_vehicle()

        if not transfer_type:
            transfer_type = self.create_transfer_type()

        return models.Pricing.objects.create(
            location=location,
            vehicle=vehicle,
            transfer_type=transfer_type,
            price=price,
        )
