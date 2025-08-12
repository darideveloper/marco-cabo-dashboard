import uuid

from django.test import TestCase

from travels import models


class TestTravelsModelBase(TestCase):
    """Base class for create travels models"""

    def __replace_random_string__(self, string: str):
        """Replace random string with a random string"""
        random_string = str(uuid.uuid4())
        return string.replace("{x}", random_string)

    def create_zone(self, name: str = "test zone {x}"):
        """Create a zone

        Args:
            name (str): Name of the zone

        Returns:
            Zone: Zone created
        """
        name = self.__replace_random_string__(name)
        return models.Zone.objects.create(name=name)

    def create_location(self, name: str = "test location {x}", zone: models.Zone = None):
        """Create a location

        Args:
            name (str): Name of the location
            zone (Zone): Zone of the location

        Returns:
            Location: Location created
        """
        name = self.__replace_random_string__(name)
        
        if not zone:
            zone = self.create_zone()

        return models.Location.objects.create(
            name=name,
            zone=zone,
        )

    def create_service_type(self, name: str = "test transfer type {x}"):
        """Create a transfer type

        Args:
            name (str): Name of the transfer type

        Returns:
            ServiceType: Transfer type created
        """
        name = self.__replace_random_string__(name)
        return models.ServiceType.objects.create(name=name)

    def create_vehicle(self, name: str = "test vehicle {x}"):
        """Create a vehicle

        Args:
            name (str): Name of the vehicle

        Returns:
            Vehicle: Vehicle created
        """
        name = self.__replace_random_string__(name)
        return models.Vehicle.objects.create(name=name)

    def create_vip_code(self, value: str = "VIP123 {x}", active: bool = True):
        """Create a VIP code

        Args:
            value (str): Value of the VIP code
            active (bool): Whether the VIP code is active

        Returns:
            VipCode: VIP code created
        """
        value = self.__replace_random_string__(value)
        return models.VipCode.objects.create(value=value, active=active)

    def create_pricing(
        self,
        location: models.Location = None,
        vehicle: models.Vehicle = None,
        service_type: models.ServiceType = None,
        price: float = 100,
    ):
        """Create a pricing

        Args:
            location (Location): Location of the pricing
            vehicle (Vehicle): Vehicle of the pricing
            service_type (ServiceType): Service type of the pricing
            price (float): Price of the pricing

        Returns:
            Pricing: Pricing created
        """

        if not location:
            location = self.create_location()

        if not vehicle:
            vehicle = self.create_vehicle()

        if not service_type:
            service_type = self.create_service_type()

        return models.Pricing.objects.create(
            location=location,
            vehicle=vehicle,
            service_type=service_type,
            price=price,
        )
