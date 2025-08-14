import json

from django.core.management import call_command
from django.conf import settings

from rest_framework import status

from core.tests_base.test_models import TestTravelsModelBase
from core.tests_base.test_views import TestApiViewsMethods
from travels import models


class ZoneViewSetTestCase(TestApiViewsMethods, TestTravelsModelBase):
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


class VehicleViewSetTestCase(TestApiViewsMethods, TestTravelsModelBase):
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

        # Validate data
        response_json = response.json()
        results = response_json["results"]
        self.assertEqual(len(results), 0)


class ServiceTypeViewSetTestCase(TestApiViewsMethods, TestTravelsModelBase):
    """Test transfer type views"""

    def setUp(self):
        super().setUp(endpoint="/api/service-types/")

    def test_get_service_types(self):
        """Test get transfer types"""

        self.create_service_type("one way")
        self.create_service_type("round trip")

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

    def test_get_service_types_no_service_type(self):
        """Test get service types with no service type"""

        # Get data and validate status code
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate data
        response_json = response.json()
        results = response_json["results"]
        self.assertEqual(len(results), 0)


class PricingViewSetTestCase(TestApiViewsMethods, TestTravelsModelBase):
    """Test pricing views"""

    def setUp(self):
        super().setUp(endpoint="/api/pricing/")

    def test_get_pricing(self):
        """Test get pricing"""

        # Create pricing
        location = self.create_location(name="location 1")
        vehicle = self.create_vehicle(name="vehicle 1")
        service_type = self.create_service_type(name="service type 1")
        self.create_pricing(
            location=location, vehicle=vehicle, service_type=service_type
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
        self.assertEqual(results[0]["service_type"]["id"], service_type.id)
        self.assertEqual(results[0]["service_type"]["name"], service_type.name)
        self.assertEqual(results[0]["price"], 100.00)

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
        self.assertEqual(results[0]["price"], 100.00)

    def test_get_pricing_filter_vehicle(self):
        """Test get pricing with vehicle filter"""

        # Create pricing with different vehicles
        vehicle1 = self.create_vehicle(name="vehicle 1")
        vehicle2 = self.create_vehicle(name="vehicle 2")
        self.create_pricing(vehicle=vehicle1)
        self.create_pricing(vehicle=vehicle2)

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
        self.assertEqual(results[0]["price"], 100.00)

    def test_get_pricing_filter_service_type(self):
        """Test get pricing with service type filter"""

        # Create pricing with different service types
        service_type1 = self.create_service_type(name="service type 1")
        service_type2 = self.create_service_type(name="service type 2")
        self.create_pricing(service_type=service_type1)
        self.create_pricing(service_type=service_type2)

        # Get data and validate status code
        response = self.client.get(self.endpoint, {"service_type": service_type1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate data
        response_json = response.json()
        results = response_json["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], 1)
        self.assertEqual(results[0]["service_type"]["id"], service_type1.id)
        self.assertEqual(results[0]["service_type"]["name"], service_type1.name)
        self.assertEqual(results[0]["price"], 100.00)

    def test_get_pricing_filter_location_vehicle_service_type(self):
        """Test get pricing with location, vehicle and service type filter"""

        # Create pricing with different location, vehicle and transfer type
        zone = self.create_zone()
        location1 = self.create_location(name="location 1", zone=zone)
        location2 = self.create_location(name="location 2", zone=zone)
        vehicle1 = self.create_vehicle(name="vehicle 1")
        vehicle2 = self.create_vehicle(name="vehicle 2")
        service_type1 = self.create_service_type(name="service type 1")
        service_type2 = self.create_service_type(name="service type 2")
        self.create_pricing(
            location=location1, vehicle=vehicle1, service_type=service_type1
        )
        self.create_pricing(
            location=location2, vehicle=vehicle2, service_type=service_type2
        )

        # Get data and validate status code
        response = self.client.get(
            self.endpoint,
            {
                "location": location1.id,
                "vehicle": vehicle1.id,
                "service_type": service_type1.id,
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
        self.assertEqual(results[0]["service_type"]["id"], service_type1.id)
        self.assertEqual(results[0]["service_type"]["name"], service_type1.name)
        self.assertEqual(results[0]["price"], 100.00)


class VipCodeValidationViewTestCase(TestApiViewsMethods, TestTravelsModelBase):
    """Test vip code validation views"""

    def setUp(self):
        super().setUp(
            endpoint="/api/validate-vip-code/",
            restricted_post=False,
            restricted_get=True,
        )

        self.vip_code = self.create_vip_code(value="VIP123", active=True)

    def test_vip_code_valid(self):
        """Test vip code valid"""

        # Send json post data and validate status code
        response = self.client.post(
            self.endpoint,
            json.dumps({"vip_code": self.vip_code.value}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate data
        response_json = response.json()
        self.assertEqual(response_json["status"], "sucess")
        self.assertEqual(response_json["message"], "VIP code is valid")
        self.assertEqual(response_json["data"], [])

    def test_vip_code_invalid(self):
        """Test vip code invalid"""

        # Send json post data and validate status code
        response = self.client.post(
            self.endpoint,
            json.dumps({"vip_code": "fake vip code"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Validate data
        response_json = response.json()
        self.assertEqual(response_json["status"], "error")
        self.assertEqual(response_json["message"], "Invalid VIP code")
        self.assertEqual(response_json["data"], [])

    def test_vip_code_invalid_inactive(self):
        """Test vip code invalid inactive"""

        # Create vip code
        self.vip_code.active = False
        self.vip_code.save()

        # Send json post data and validate status code
        response = self.client.post(self.endpoint, {"vip_code": self.vip_code.value})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Validate data
        response_json = response.json()
        self.assertEqual(response_json["status"], "error")
        self.assertEqual(response_json["message"], "Invalid VIP code")
        self.assertEqual(response_json["data"], [])

    def test_vip_code_no_value(self):
        """Test vip code invalid empty"""

        # Send json post data and validate status code
        response = self.client.post(
            self.endpoint,
            json.dumps({"vip_code": ""}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Validate data
        response_json = response.json()
        self.assertEqual(response_json["status"], "error")
        self.assertEqual(response_json["message"], "Invalid VIP code")
        self.assertEqual(response_json["data"], [])

    def test_vip_code_missing_data(self):
        """Test vip code no data"""

        # Send json post data and validate status code
        response = self.client.post(
            self.endpoint,
            json.dumps({"invalid_key": "invalid_value"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Validate data
        response_json = response.json()
        self.assertEqual(response_json["status"], "error")
        self.assertEqual(response_json["message"], "Invalid VIP code")
        self.assertEqual(response_json["data"], [])


class SaleViewSetTestCase(TestApiViewsMethods, TestTravelsModelBase):
    """Test sale views"""

    @classmethod
    def setUpTestData(cls):
        # Create db
        call_command("apps_loaddata")
        call_command("load_pricing")

    def setUp(self):
        super().setUp(
            endpoint="/api/sales/", restricted_post=False, restricted_get=True
        )

        # Api missing data
        self.data = {
            "service_type": 1,
            "client_name": "John",
            "client_last_name": "Doe",
            "client_email": "john.doe@example.com",
            "client_phone": "1234567890",
            "passengers": 4,
            "location": 1,
            "vip_code": "",
            "arrival_date": "2025-01-01",
            "arrival_time": "10:00",
            "arrival_airline": "Airline",
            "arrival_flight_number": "1234567890",
            "departure_date": "2025-01-01",
            "departure_time": "10:00",
            "departure_airline": "Airline",
            "departure_flight_number": "1234567890",
            "vehicle": 1,
        }

    def validate_no_data_created(self):
        """Validate no data created"""
        self.assertEqual(models.Sale.objects.count(), 0)
        self.assertEqual(models.Client.objects.count(), 0)
        self.assertEqual(models.Transfer.objects.count(), 0)

    def test_post_missing_data(self):
        """Test post missing data
        Expected: Missing required fields
        """

        # Send json post data and validate status code
        response = self.client.post(self.endpoint, content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Validate data
        response_json = response.json()
        self.assertEqual(response_json["status"], "error")
        self.assertEqual(response_json["message"], "Invalid sale data")
        required_fields = [
            "service_type",
            "client_name",
            "client_last_name",
            "client_email",
            "client_phone",
            "passengers",
            "location",
            "arrival_date",
            "arrival_time",
            "arrival_airline",
            "arrival_flight_number",
            "vehicle",
        ]
        for field in required_fields:
            self.assertIn(field, response_json["errors"])
            self.assertIn("Este campo es requerido.", response_json["errors"][field])

        # Validate no data created
        self.validate_no_data_created()

    def test_post_service_type_invalid(self):
        """Test post invalid service type
        Expected: service_type not found
        """

        # Change service type
        service_type_invalid = 99
        self.data["service_type"] = service_type_invalid

        # Send json post data and validate status code
        response = self.client.post(
            self.endpoint, json.dumps(self.data), content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Validate data
        response_json = response.json()
        self.assertEqual(response_json["status"], "error")
        self.assertEqual(response_json["message"], "Invalid sale data")
        self.assertIn("service_type", response_json["errors"])
        self.assertIn(
            f'Clave primaria "{service_type_invalid}" inválida - objeto no existe.',
            response_json["errors"]["service_type"],
        )

        # Validate no data created
        self.validate_no_data_created()

    def test_post_location_invalid(self):
        """Test post invalid location
        Expected: location not found
        """

        # Change location
        location_invalid = 999
        self.data["location"] = location_invalid

        # Send json post data and validate status code
        response = self.client.post(
            self.endpoint, json.dumps(self.data), content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Validate data
        response_json = response.json()
        self.assertEqual(response_json["status"], "error")
        self.assertEqual(response_json["message"], "Invalid sale data")
        self.assertIn("location", response_json["errors"])
        self.assertIn(
            f'Clave primaria "{location_invalid}" inválida - objeto no existe.',
            response_json["errors"]["location"],
        )

        # Validate no data created
        self.validate_no_data_created()

    def test_post_vip_code_invalid(self):
        """Test post invalid vip code
        Expected: vip code not found
        """

        # Change vip code
        vip_code = "fake vip code"
        self.data["vip_code"] = vip_code

        # Send json post data and validate status code
        response = self.client.post(
            self.endpoint, json.dumps(self.data), content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Validate data
        response_json = response.json()
        self.assertEqual(response_json["status"], "error")
        self.assertEqual(response_json["message"], "Invalid sale data")
        self.assertIn("vip_code", response_json["errors"])
        self.assertIn(
            f"Objeto con value={vip_code} no existe.",
            response_json["errors"]["vip_code"],
        )

        # Validate no data created
        self.validate_no_data_created()

    def test_post_vip_code_inactive(self):
        """Test post inactive vip code
        Expected: vip code not found
        """

        # Change vip code
        vip_code = "VIP123"
        self.create_vip_code(value=vip_code, active=False)
        self.data["vip_code"] = vip_code

        # Send json post data and validate status code
        response = self.client.post(
            self.endpoint, json.dumps(self.data), content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Validate data
        response_json = response.json()
        self.assertEqual(response_json["status"], "error")
        self.assertEqual(response_json["message"], "Invalid sale data")
        self.assertIn("vip_code", response_json["errors"])
        self.assertIn(
            f"Objeto con value={vip_code} no existe.",
            response_json["errors"]["vip_code"],
        )

        # Validate no data created
        self.validate_no_data_created()

    def test_post_vip_code_empty(self):
        """Test post empty vip code
        Expected: ok
        """

        # Change vip code
        self.data["vip_code"] = ""

        # Send json post data and validate status code
        response = self.client.post(
            self.endpoint, json.dumps(self.data), content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Validate data
        response_json = response.json()
        self.assertEqual(response_json["status"], "success")
        self.assertEqual(response_json["message"], "Sale created successfully")

    def test_post_vip_code_missing(self):
        """Test post missing vip code
        Expected: ok
        """

        # Remove vip code from data if exists
        if "vip_code" in self.data:
            del self.data["vip_code"]

        # Send json post data and validate status code
        response = self.client.post(
            self.endpoint, json.dumps(self.data), content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Validate data
        response_json = response.json()
        self.assertEqual(response_json["status"], "success")
        self.assertEqual(response_json["message"], "Sale created successfully")

    def test_post_vehicle_invalid(self):
        """Test post invalid vehicle
        Expected: vehicle not found
        """

        # Change vehicle
        vehicle_invalid = 999
        self.data["vehicle"] = vehicle_invalid

        # Send json post data and validate status code
        response = self.client.post(
            self.endpoint, json.dumps(self.data), content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Validate data
        response_json = response.json()
        self.assertEqual(response_json["status"], "error")
        self.assertEqual(response_json["message"], "Invalid sale data")
        self.assertIn("vehicle", response_json["errors"])
        self.assertIn(
            f'Clave primaria "{vehicle_invalid}" inválida - objeto no existe.',
            response_json["errors"]["vehicle"],
        )

        # Validate no data created
        self.validate_no_data_created()

    def test_post_ok_one_way(self):
        """Test post ok one way
        Expected: ok
        """

        # Change service type
        del self.data["departure_date"]
        del self.data["departure_time"]
        del self.data["departure_airline"]
        del self.data["departure_flight_number"]

        # Send json post data and validate status code
        response = self.client.post(
            self.endpoint, json.dumps(self.data), content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Validate data
        response_json = response.json()
        self.assertEqual(response_json["status"], "success")
        self.assertEqual(response_json["message"], "Sale created successfully")
        self.assertTrue(
            response_json["data"]["payment_link"].startswith(
                "https://checkout.stripe.com/"
            )
        )

        # Validate data created
        client = models.Client.objects.get(email=self.data["client_email"])
        self.assertEqual(client.name, self.data["client_name"])
        self.assertEqual(client.last_name, self.data["client_last_name"])
        self.assertEqual(client.email, self.data["client_email"])
        self.assertEqual(client.phone, self.data["client_phone"])

        sale = models.Sale.objects.get(client=client)
        self.assertEqual(sale.service_type.name, "One Way")
        self.assertEqual(sale.location.name, "Alegranza")  # csv data
        self.assertEqual(sale.vip_code, None)
        self.assertEqual(sale.vehicle.name, "Suburban")  # fixtures data
        self.assertEqual(sale.passengers, 4)

        transfer_arrival = models.Transfer.objects.get(sale=sale, type="arrival")
        self.assertEqual(transfer_arrival.date.strftime("%Y-%m-%d"), "2025-01-01")
        self.assertEqual(transfer_arrival.hour.strftime("%H:%M"), "10:00")
        self.assertEqual(transfer_arrival.airline, "Airline")
        self.assertEqual(transfer_arrival.flight_number, "1234567890")

        # Validate no departure data
        transfers_departure = models.Transfer.objects.filter(
            sale=sale, type="departure"
        )
        self.assertEqual(len(transfers_departure), 0)

        # Validate total calculation (with csv pricing data )
        self.assertEqual(sale.total, 90.00)

    def test_post_ok_round_trip(self):
        """Test post ok round trip
        Expected: ok
        """

        # Set service type to round trip
        self.data["service_type"] = 2

        # Send json post data and validate status code
        response = self.client.post(
            self.endpoint, json.dumps(self.data), content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Validate data
        response_json = response.json()
        self.assertEqual(response_json["status"], "success")
        self.assertEqual(response_json["message"], "Sale created successfully")
        self.assertTrue(
            response_json["data"]["payment_link"].startswith(
                "https://checkout.stripe.com/"
            )
        )

        # Validate data created
        client = models.Client.objects.get(email=self.data["client_email"])
        self.assertEqual(client.name, self.data["client_name"])
        self.assertEqual(client.last_name, self.data["client_last_name"])
        self.assertEqual(client.email, self.data["client_email"])
        self.assertEqual(client.phone, self.data["client_phone"])

        sale = models.Sale.objects.get(client=client)
        self.assertEqual(sale.service_type.name, "Round Trip")
        self.assertEqual(sale.location.name, "Alegranza")  # csv data
        self.assertEqual(sale.vip_code, None)
        self.assertEqual(sale.vehicle.name, "Suburban")  # fixtures data
        self.assertEqual(sale.passengers, 4)

        transfer_arrival = models.Transfer.objects.get(sale=sale, type="arrival")
        self.assertEqual(transfer_arrival.date.strftime("%Y-%m-%d"), "2025-01-01")
        self.assertEqual(transfer_arrival.hour.strftime("%H:%M"), "10:00")
        self.assertEqual(transfer_arrival.airline, "Airline")
        self.assertEqual(transfer_arrival.flight_number, "1234567890")

        # Validate departure data
        transfer_departure = models.Transfer.objects.get(sale=sale, type="departure")
        self.assertEqual(transfer_departure.date.strftime("%Y-%m-%d"), "2025-01-01")
        self.assertEqual(transfer_departure.hour.strftime("%H:%M"), "10:00")
        self.assertEqual(transfer_departure.airline, "Airline")
        self.assertEqual(transfer_departure.flight_number, "1234567890")

        # Validate total calculation (with csv pricing data)
        self.assertEqual(sale.total, 170.00)

    def test_post_ok_one_way_vip_code(self):
        """Test post ok one way with vip code
        Expected: ok
        """

        # Create vip code
        vip_code = "VIP123"
        self.create_vip_code(value=vip_code, active=True)

        # Set vip code
        self.data["vip_code"] = vip_code

        # Send json post data and validate status code
        response = self.client.post(
            self.endpoint, json.dumps(self.data), content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Validate data
        response_json = response.json()
        self.assertEqual(response_json["status"], "success")
        self.assertEqual(response_json["message"], "Sale created successfully")
        self.assertEqual(
            response_json["data"]["payment_link"],
            settings.LANDING_HOST + "/?status=done",
        )

    def test_post_ok_round_trip_vip_code(self):
        """Test post ok round trip with vip code
        Expected: ok
        """

        # Set service type to round trip
        self.data["service_type"] = 2
        
        # Create vip code
        vip_code = "VIP123"
        self.create_vip_code(value=vip_code, active=True)
        
        # Set vip code
        self.data["vip_code"] = vip_code
        
        # Send json post data and validate status code
        response = self.client.post(
            self.endpoint, json.dumps(self.data), content_type="application/json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Validate data
        response_json = response.json()
        self.assertEqual(response_json["status"], "success")
        self.assertEqual(response_json["message"], "Sale created successfully")
        self.assertEqual(
            response_json["data"]["payment_link"],
            settings.LANDING_HOST + "/?status=done",
        )