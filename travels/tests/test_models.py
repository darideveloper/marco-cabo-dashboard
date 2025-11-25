from travels import models

from core.tests_base.test_models import TestTravelsModelBase


class ZoneTestCase(TestTravelsModelBase):
    """Test travels models"""

    def setUp(self):
        super().setUp()

    def test_property_locations(self):
        """Test zone location as a property"""

        zone = self.create_zone()
        for _ in range(10):
            self.create_location(zone=zone)

        self.assertEqual(zone.locations.count(), 10)
        self.assertTrue(isinstance(zone.locations[0], models.Location))


class SaleTestCase(TestTravelsModelBase):
    """Test travels models"""

    def setUp(self):
        super().setUp()

    def test_get_summary(self):
        """Test sale summary method"""

        # Create a sale
        sale = self.create_sale()
        arrival_transfer = self.create_transfer(sale=sale)
        summary = sale.get_summary()
        
        # Validate summary data
        self.assertIn("Mar Co. Cabo", summary)
        self.assertIn(sale.client.name, summary)
        self.assertIn(sale.client.last_name, summary)
        self.assertIn(sale.client.email, summary)
        self.assertIn(sale.client.phone, summary)
        self.assertIn(sale.vehicle.name, summary)
        self.assertIn(sale.service_type.name, summary)
        self.assertIn(sale.location.zone.name, summary)
        self.assertIn(sale.location.name, summary)
        self.assertIn(f"{sale.passengers} passengers", summary)
        self.assertIn(sale.vip_code.value, summary)
        self.assertIn(str(sale.total), summary)
        self.assertIn(arrival_transfer.date.strftime("%Y-%m-%d"), summary)
        self.assertIn(arrival_transfer.hour.strftime("%H:%M"), summary)
        self.assertIn(arrival_transfer.airline, summary)
        self.assertIn(arrival_transfer.flight_number, summary)
        
    def test_get_summary_no_vip_code(self):
        """Test sale summary method"""

        # Create a sale
        sale = self.create_sale(auto_create_vip_code=False)
        summary = sale.get_summary()
        
        # Validate summary data
        self.assertIn("No VIP", summary)
        
    def test_get_summary_with_departure_transfer(self):
        """Test sale summary method with departure transfer"""

        # Create a sale
        sale = self.create_sale()
        arrival_transfer = self.create_transfer(sale=sale)
        departure_transfer = self.create_transfer(sale=sale, type="departure")
        summary = sale.get_summary()
        
        # Validate summary data
        self.assertIn(departure_transfer.date.strftime("%Y-%m-%d"), summary)
        self.assertIn(departure_transfer.hour.strftime("%H:%M"), summary)
        self.assertIn(departure_transfer.airline, summary)
        self.assertIn(departure_transfer.flight_number, summary)
        self.assertIn(arrival_transfer.date.strftime("%Y-%m-%d"), summary)
        self.assertIn(arrival_transfer.hour.strftime("%H:%M"), summary)
        self.assertIn(arrival_transfer.airline, summary)
        self.assertIn(arrival_transfer.flight_number, summary)