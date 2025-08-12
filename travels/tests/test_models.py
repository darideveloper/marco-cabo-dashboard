from travels import models

from core.tests_base.test_models import TestTravelsModelBase


class ZoneTestCase(TestTravelsModelBase):
    """Test travels models"""

    def setUp(self):
        super().setUp()

    def test_property_locations(self):
        """Test location property"""
        zone = self.create_zone()
        for _ in range(10):
            self.create_location(zone=zone)
            
        self.assertEqual(zone.locations.count(), 10)
        self.assertTrue(isinstance(zone.locations[0], models.Location))