from rest_framework import status

from core.tests_base.test_views import TestApiViewsMethods
from core.tests_base.test_models import TestTravelsModelBase


class TestZoneViewSet(TestApiViewsMethods, TestTravelsModelBase):
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
            json_location = list(
                filter(lambda row: row["id"] == location.id, json_locations)
            )[0]
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


class TestVehicleViewSet(TestApiViewsMethods, TestTravelsModelBase):
    """Test vehicle views"""

    def setUp(self):
        super().setUp(endpoint="/api/vehicles/")

    def test_get_vehicles(self):
        """Test get vehicles"""

        self.create_vehicle("suburban")
        self.create_vehicle("van")
        self.create_vehicle("sprinter")

        # Get data and validate status code
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate data
        response_json = response.json()
        results = response_json["results"]
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]["id"], 1)
        self.assertEqual(results[0]["name"], "suburban")
        self.assertEqual(results[1]["id"], 2)
        self.assertEqual(results[1]["name"], "van")
        self.assertEqual(results[2]["id"], 3)
        self.assertEqual(results[2]["name"], "sprinter")

    def test_get_vehicles_no_vehicle(self):
        """Test get vehicles with no vehicle"""

        # Get data and validate status code
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class TestTransferTypeViewSet(TestApiViewsMethods, TestTravelsModelBase):
    """Test transfer type views"""

    def setUp(self):
        super().setUp(endpoint="/api/transfer-types/")

    def test_get_transfer_types(self):
        """Test get transfer types"""

        self.create_transfer_type("one way")
        self.create_transfer_type("round trip")

        # Get data and validate status code
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate data
        response_json = response.json()
        results = response_json["results"]
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["id"], 1)
        self.assertEqual(results[0]["name"], "one way")
        self.assertEqual(results[1]["id"], 2)
        self.assertEqual(results[1]["name"], "round trip")

    def test_get_transfer_types_no_transfer_type(self):
        """Test get transfer types with no transfer type"""

        # Get data and validate status code
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate data
        response_json = response.json()
        results = response_json["results"]
        self.assertEqual(len(results), 0)


class TestPricingViewSet(TestApiViewsMethods, TestTravelsModelBase):
    """Test pricing views"""

    def setUp(self):
        super().setUp(endpoint="/api/pricing/")

    def test_get_pricing(self):
        """Test get pricing"""

        # Create pricing
        location = self.create_location(name="location 1")
        vehicle = self.create_vehicle(name="vehicle 1")
        transfer_type = self.create_transfer_type(name="transfer type 1")
        self.create_pricing(
            location=location, vehicle=vehicle, transfer_type=transfer_type
        )

        # Get data and validate status code
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate data
        response_json = response.json()
        results = response_json["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], 1)
        self.assertEqual(results[0]["location"]["id"], location.id)
        self.assertEqual(results[0]["location"]["name"], location.name)
        self.assertEqual(results[0]["vehicle"]["id"], vehicle.id)
        self.assertEqual(results[0]["vehicle"]["name"], vehicle.name)
        self.assertEqual(results[0]["transfer_type"]["id"], transfer_type.id)
        self.assertEqual(results[0]["transfer_type"]["name"], transfer_type.name)
        self.assertEqual(results[0]["price"], "100.00")

    def test_get_pricing_filter_location(self):
        """Test get pricing with location filter"""

        # Create pricing with different locations
        zone = self.create_zone()
        location1 = self.create_location(name="location 1", zone=zone)
        location2 = self.create_location(name="location 2", zone=zone)
        self.create_pricing(location=location1)
        self.create_pricing(location=location2)

        # Get data and validate status code
        response = self.client.get(self.endpoint, {"location": location1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate data
        response_json = response.json()
        results = response_json["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], 1)
        self.assertEqual(results[0]["location"]["id"], location1.id)
        self.assertEqual(results[0]["location"]["name"], location1.name)

    def test_get_pricing_filter_vehicle(self):
        """Test get pricing with vehicle filter"""

        # Create pricing with different vehicles
        location = self.create_location(name="location 1")
        vehicle1 = self.create_vehicle(name="vehicle 1")
        vehicle2 = self.create_vehicle(name="vehicle 2")
        self.create_pricing(location=location, vehicle=vehicle1)
        self.create_pricing(location=location, vehicle=vehicle2)

        # Get data and validate status code
        response = self.client.get(self.endpoint, {"vehicle": vehicle1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate data
        response_json = response.json()
        results = response_json["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], 1)
        self.assertEqual(results[0]["vehicle"]["id"], vehicle1.id)
        self.assertEqual(results[0]["vehicle"]["name"], vehicle1.name)

    def test_get_pricing_filter_transfer_type(self):
        """Test get pricing with transfer type filter"""

        # Create pricing with different transfer types
        location = self.create_location(name="location 1")
        transfer_type1 = self.create_transfer_type(name="transfer type 1")
        transfer_type2 = self.create_transfer_type(name="transfer type 2")
        self.create_pricing(location=location, transfer_type=transfer_type1)
        self.create_pricing(location=location, transfer_type=transfer_type2)

        # Get data and validate status code
        response = self.client.get(self.endpoint, {"transfer_type": transfer_type1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate data
        response_json = response.json()
        results = response_json["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], 1)
        self.assertEqual(results[0]["transfer_type"]["id"], transfer_type1.id)
        self.assertEqual(results[0]["transfer_type"]["name"], transfer_type1.name)

    def test_get_pricing_filter_location_vehicle_transfer_type(self):
        """Test get pricing with location, vehicle and transfer type filter"""

        # Create pricing with different location, vehicle and transfer type
        zone = self.create_zone()
        location1 = self.create_location(name="location 1", zone=zone)
        location2 = self.create_location(name="location 2", zone=zone)
        vehicle1 = self.create_vehicle(name="vehicle 1")
        vehicle2 = self.create_vehicle(name="vehicle 2")
        transfer_type1 = self.create_transfer_type(name="transfer type 1")
        transfer_type2 = self.create_transfer_type(name="transfer type 2")
        self.create_pricing(
            location=location1, vehicle=vehicle1, transfer_type=transfer_type1
        )
        self.create_pricing(
            location=location2, vehicle=vehicle2, transfer_type=transfer_type2
        )

        # Get data and validate status code
        response = self.client.get(
            self.endpoint,
            {
                "location": location1.id,
                "vehicle": vehicle1.id,
                "transfer_type": transfer_type1.id,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate data
        response_json = response.json()
        results = response_json["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], 1)
        self.assertEqual(results[0]["location"]["id"], location1.id)
        self.assertEqual(results[0]["location"]["name"], location1.name)
        self.assertEqual(results[0]["vehicle"]["id"], vehicle1.id)
        self.assertEqual(results[0]["vehicle"]["name"], vehicle1.name)
        self.assertEqual(results[0]["transfer_type"]["id"], transfer_type1.id)
        self.assertEqual(results[0]["transfer_type"]["name"], transfer_type1.name)
