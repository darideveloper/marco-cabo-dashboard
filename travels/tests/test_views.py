from rest_framework import status

from core.tests_base.test_views import TestTravelViewsBase


class TestZoneViews(TestTravelViewsBase):
    """Test zone views"""

    def setUp(self):
        super().setUp(endpoint="/api/zones/")

    def test_get_zones(self):
        """Test get zones with location"""

        # Create zone with 3 locations
        zone = self.create_zone()
        locations = []
        for index in range(3):
            location = self.create_location(zone=zone, name=f"location {index}")
            locations.append(location)

        # Get data and validate status code
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate data
        response_json = response.json()
        results = response_json["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], zone.id)
        self.assertEqual(results[0]["name"], zone.name)
        self.assertEqual(len(results[0]["locations"]), 3)
        json_locations = results[0]["locations"]
        for location in locations:
            json_location = list(filter(
                lambda row: row["id"] == location.id, json_locations
            ))[0]
            self.assertIsNotNone(json_location)
            self.assertEqual(json_location["name"], location.name)
            
    def test_get_zones_no_location(self):
        """Test get zones with no location"""

        # Create zone with no location
        zone = self.create_zone()

        # Get data and validate status code
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Validate data
        response_json = response.json()
        results = response_json["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], zone.id)
        self.assertEqual(len(results[0]["locations"]), 0)
