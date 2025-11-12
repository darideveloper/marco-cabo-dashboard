import uuid
import datetime

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

    def create_location(
        self, name: str = "test location {x}", zone: models.Zone = None
    ):
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

    def create_vehicle(self, name: str = "test vehicle {x}", passengers: int = 0):
        """Create a vehicle

        Args:
            name (str): Name of the vehicle

        Returns:
            Vehicle: Vehicle created
        """
        name = self.__replace_random_string__(name)
        return models.Vehicle.objects.create(name=name, passengers=passengers)

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

    def create_client(
        self,
        name: str = "test client {x}",
        last_name: str = "test last name {x}",
        email: str = "test@test.com",
        phone: str = "1234567890",
    ):
        """Create a client

        Args:
            name (str): Name of the client
            last_name (str): Last name of the client
            email (str): Email of the client
            phone (str): Phone of the client

        Returns:
            Client: Client created
        """

        # Replace random strings
        name = self.__replace_random_string__(name)
        last_name = self.__replace_random_string__(last_name)
        email = self.__replace_random_string__(email)
        phone = self.__replace_random_string__(phone)

        # Create client
        return models.Client.objects.create(
            name=name, last_name=last_name, email=email, phone=phone
        )

    def create_sale(
        self,
        client: models.Client = None,
        # vip_code: models.VipCode = None,
        vehicle: models.Vehicle = None,
        passengers: int = 1,
        service_type: models.ServiceType = None,
        location: models.Location = None,
        total: float = 100,
        paid: bool = False,
        # auto_create_vip_code: bool = True,
    ):
        """Create a sale

        Args:
            client (Client): Client of the sale
            vip_code (VipCode): VIP code of the sale
            vehicle (Vehicle): Vehicle of the sale
            passengers (int): Passengers of the sale
            service_type (ServiceType): Service type of the sale
            location (Location): Location of the sale
            stripe_code (str): Stripe code of the sale
            total (float): Total of the sale
            paid (bool): Whether the sale is paid
            auto_create_vip_code (bool): Whether to create a VIP code automatically
        """

        if not client:
            client = self.create_client()

        # if not vip_code and auto_create_vip_code:
        #     vip_code = self.create_vip_code()

        if not vehicle:
            vehicle = self.create_vehicle()

        if not service_type:
            service_type = self.create_service_type()

        if not location:
            location = self.create_location()

        return models.Sale.objects.create(
            client=client,
            # vip_code=vip_code,
            vehicle=vehicle,
            passengers=passengers,
            service_type=service_type,
            location=location,
            total=total,
            paid=paid,
        )

    def create_transfer(
        self,
        date: datetime.datetime = datetime.datetime.now().date(),
        hour: datetime.time = datetime.time(10, 0, 0),
        type: str = "arrival",
        sale: models.Sale = None,
        airline: str = "test airline {x}",
        flight_number: str = "test flight number {x}",
    ):
        """Create a transfer

        Args:
            date (datetime.datetime): Date of the transfer
            hour (datetime.time): Hour of the transfer
            type (str): Type of the transfer
            sale (Sale): Sale of the transfer
            airline (str): Airline of the transfer
            flight_number (str): Flight number of the transfer
        """
        
        if not sale:
            sale = self.create_sale()

        # Replace random strings
        airline = self.__replace_random_string__(airline)
        flight_number = self.__replace_random_string__(flight_number)

        # Create transfer
        return models.Transfer.objects.create(
            date=date,
            hour=hour,
            type=type,
            sale=sale,
            airline=airline,
            flight_number=flight_number,
        )
            
