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
    
    