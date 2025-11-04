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
        summary = sale.get_summary()
        
        # Validate summary data
        self.assertIn("Marco Cabo", summary)
        self.assertIn(sale.vehicle.name, summary)
        self.assertIn(sale.client.email, summary)
        self.assertIn(sale.location.zone.name, summary)
        self.assertIn(sale.location.name, summary)
        self.assertIn(sale.service_type.name, summary)
        self.assertIn(str(sale.total), summary)