import json
from time import sleep

from django.core.management import call_command
from django.conf import settings
from django.contrib.auth.models import User

from rest_framework import status

from core.tests_base.test_models import TestTravelsModelBase
from core.tests_base.test_views import TestApiViewsMethods, TestSeleniumBase
from travels import models


class HotelsViewSetTestCase(TestApiViewsMethods, TestTravelsModelBase):
    """Test hotels views"""

    def setUp(self):
        super().setUp(endpoint="/api/hotels/")

    def test_get_hotels(self):
        """Test get hotels with location"""

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

    def test_get_hotels_no_location(self):
        """Test get hotels with no location"""

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


class PostalCodeViewSetTestCase(TestApiViewsMethods, TestTravelsModelBase):
    """Test postal code views"""

    def setUp(self):
        super().setUp(endpoint="/api/postal-codes/")

    def test_get_postal_codes(self):
        """Test get postal codes with location"""

        # Create zone with 3 locations
        zone = self.create_zone(name="Codigo Postal")
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
        self.assertEqual(len(results), 3)
        for location in locations:
            json_location = list(filter(lambda row: row["id"] == location.id, results))[
                0
            ]
            self.assertIsNotNone(json_location)
            self.assertEqual(json_location["id"], location.id)
            self.assertEqual(json_location["name"], location.name)

    def test_get_postal_codes_no_location(self):
        """Test get postal codes with no location"""

        # Create zone with no location
        self.create_zone(name="Codigo Postal")

        # Get data and validate status code
        response = self.client.get(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate data
        response_json = response.json()
        results = response_json["results"]
        self.assertEqual(len(results), 0)


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


# class VipCodeValidationViewTestCase(TestApiViewsMethods, TestTravelsModelBase):
#     """Test vip code validation views"""

#     def setUp(self):
#         super().setUp(
#             endpoint="/api/validate-vip-code/",
#             restricted_post=False,
#             restricted_get=True,
#         )

#         self.vip_code = self.create_vip_code(value="VIP123", active=True)

#     def test_vip_code_valid(self):
#         """Test vip code valid"""

#         # Send json post data and validate status code
#         response = self.client.post(
#             self.endpoint,
#             json.dumps({"vip_code": self.vip_code.value}),
#             content_type="application/json",
#         )
#         self.assertEqual(response.status_code, status.HTTP_200_OK)

#         # Validate data
#         response_json = response.json()
#         self.assertEqual(response_json["status"], "sucess")
#         self.assertEqual(response_json["message"], "VIP code is valid")
#         self.assertEqual(response_json["data"], [])

#     def test_vip_code_invalid(self):
#         """Test vip code invalid"""

#         # Send json post data and validate status code
#         response = self.client.post(
#             self.endpoint,
#             json.dumps({"vip_code": "fake vip code"}),
#             content_type="application/json",
#         )
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#         # Validate data
#         response_json = response.json()
#         self.assertEqual(response_json["status"], "error")
#         self.assertEqual(response_json["message"], "Invalid VIP code")
#         self.assertEqual(response_json["data"], [])

#     def test_vip_code_invalid_inactive(self):
#         """Test vip code invalid inactive"""

#         # Create vip code
#         self.vip_code.active = False
#         self.vip_code.save()

#         # Send json post data and validate status code
#         response = self.client.post(self.endpoint, {"vip_code": self.vip_code.value})
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#         # Validate data
#         response_json = response.json()
#         self.assertEqual(response_json["status"], "error")
#         self.assertEqual(response_json["message"], "Invalid VIP code")
#         self.assertEqual(response_json["data"], [])

#     def test_vip_code_no_value(self):
#         """Test vip code invalid empty"""

#         # Send json post data and validate status code
#         response = self.client.post(
#             self.endpoint,
#             json.dumps({"vip_code": ""}),
#             content_type="application/json",
#         )
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#         # Validate data
#         response_json = response.json()
#         self.assertEqual(response_json["status"], "error")
#         self.assertEqual(response_json["message"], "Invalid VIP code")
#         self.assertEqual(response_json["data"], [])

#     def test_vip_code_missing_data(self):
#         """Test vip code no data"""

#         # Send json post data and validate status code
#         response = self.client.post(
#             self.endpoint,
#             json.dumps({"invalid_key": "invalid_value"}),
#             content_type="application/json",
#         )
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#         # Validate data
#         response_json = response.json()
#         self.assertEqual(response_json["status"], "error")
#         self.assertEqual(response_json["message"], "Invalid VIP code")
#         self.assertEqual(response_json["data"], [])


class SaleViewSetTestCase(TestApiViewsMethods, TestTravelsModelBase):
    """Test sale views"""

    @classmethod
    def setUpTestData(cls):
        # Create db
        call_command("apps_loaddata")
        call_command("load_pricing")

    def setUp(self):
        super().setUp(
            endpoint="/api/sales/", restricted_post=False, restricted_get=False
        )

        # Api data
        self.data = {
            "service_type": 1,
            "client_name": "John",
            "client_email": "john.doe@example.com",
            "location": 1,
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
            "client_email",
            "location",
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
        self.assertEqual(client.last_name, None)
        self.assertEqual(client.email, self.data["client_email"])
        self.assertEqual(client.phone, None)

        sale = models.Sale.objects.get(client=client)
        self.assertEqual(sale.service_type.name, "One Way")
        self.assertEqual(sale.location.name, "Alegranza")  # csv data
        self.assertEqual(sale.vehicle.name, "Suburban")  # fixtures data

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
        self.assertEqual(client.last_name, None)
        self.assertEqual(client.email, self.data["client_email"])
        self.assertEqual(client.phone, None)

        sale = models.Sale.objects.get(client=client)
        self.assertEqual(sale.service_type.name, "Round Trip")
        self.assertEqual(sale.location.name, "Alegranza")  # csv data
        self.assertEqual(sale.vehicle.name, "Suburban")  # fixtures data

        # Validate total calculation (with csv pricing data)
        self.assertEqual(sale.total, 170.00)
        
    def test_get_sale_not_found(self):
        """Test get sale done with sale not found
        Expected: error redirect
        """

        # Get data and validate status code
        endpoint = f"{self.endpoint}invalid/"
        response = self.client.get(endpoint)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Validate error
        response_json = response.json()
        self.assertEqual(response_json["status"], "error")
        self.assertEqual(response_json["message"], "Sale not found")
        self.assertEqual(response_json["data"], {})
        
    def test_get_sale_found(self):
        """Test get sale done with sale found
        Expected: success redirect
        """
        
        # Create a sale
        sale = self.create_sale()

        # Get data and validate status code
        endpoint = f"{self.endpoint}{sale.stripe_code}/"
        response = self.client.get(endpoint)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate error
        response_json = response.json()
        self.assertEqual(response_json["status"], "success")
        self.assertEqual(response_json["message"], "Sale data retrieved successfully")
        self.assertEqual(response_json["data"]["id"], sale.id)
        self.assertEqual(response_json["data"]["service_type"]["name"], sale.service_type.name)
        self.assertEqual(response_json["data"]["location"]["name"], sale.location.name)
        self.assertEqual(response_json["data"]["vehicle"]["name"], sale.vehicle.name)
        self.assertEqual(response_json["data"]["total"], sale.total)
        self.assertEqual(response_json["data"]["stripe_code"], str(sale.stripe_code))
        self.assertEqual(response_json["data"]["client"]["name"], sale.client.name)
        self.assertEqual(response_json["data"]["client"]["email"], sale.client.email)


class SaleViewSetLiveTestCase(TestSeleniumBase):
    """Test sale view set live"""

    def setUp(self):
        endpoint = "/api/sales/"
        super().setUp(endpoint=endpoint)

        # Create user and login to api
        username = "test_user"
        password = "test_pass"
        User.objects.create_superuser(
            username=username,
            email="test@gmail.com",
            password=password,
        )
        self.client.login(username=username, password=password)

        # Create db
        call_command("apps_loaddata")
        call_command("load_pricing")

        # Create sale
        self.sale_data = {
            "client_name": "John",
            "client_email": "john.doe@example.com",
            "service_type": 2,
            "location": 1,
            "vehicle": 1,
        }

        self.stripe_data = {
            "amount": 170,  # amount from pricing csv
            "name": "John",
            "card": {
                "number": "4242424242424242",
                "exp": "12 / 34",
                "cvc": "123",
            },
            "phone": "4493402611",
        }

        self.selectors = {
            "phone": 'input[name="phoneNumber"]',
            "card_number": "input[name='cardNumber']",
            "card_date": "input[name='cardExpiry']",
            "card_cvc": "input[name='cardCvc']",
            "card_name": "input[name='billingName']",
            "card_submit": "button.SubmitButton",
            "amount": "span.CurrencyAmount",
            "back_button": 'a[data-testid="business-link"]',
        }

    def load_stripe(self):
        """Get payment link"""

        # Get payment link
        response = self.client.post(
            self.endpoint, json.dumps(self.sale_data), content_type="application/json"
        )

        # Validate data
        response_json = response.json()
        self.assertEqual(response_json["status"], "success")
        self.assertEqual(response_json["message"], "Sale created successfully")
        payment_link = response_json["data"]["payment_link"]

        # Open payment link
        self.driver.get(payment_link)
        sleep(4)

    def test_stripe_amount(self):
        """Test stripe amount is correct
        Expected: ok
        """

        # Load stripe page
        self.load_stripe()

        # Validate stripe amount
        fields = self.get_selenium_elems(self.selectors)
        amount = fields["amount"].text
        self.assertEqual(amount, f"${self.stripe_data['amount']}.00")

    def test_stripe_sucess_payment(self):
        """Test stripe success payment
        Expected: redirect to confirmation page
        """

        # Load stripe pageº
        self.load_stripe()

        fields = self.get_selenium_elems(self.selectors)

        # fill phone number
        fields["phone"].send_keys(self.stripe_data["phone"])

        # Fill payment data
        fields["card_number"].send_keys(self.stripe_data["card"]["number"])
        fields["card_date"].send_keys(self.stripe_data["card"]["exp"])
        fields["card_cvc"].send_keys(self.stripe_data["card"]["cvc"])
        fields["card_name"].send_keys(self.stripe_data["name"])

        # Submit form
        self.click_js_elem(fields["card_submit"])
        sleep(6)

        # Validate redirect to confirmation page after pay
        sale = models.Sale.objects.get(client__email=self.sale_data["client_email"])
        confirmation_url = self.driver.current_url.replace(settings.LANDING_HOST_SUCCESS, "")
        self.assertIn(f"/confirmation/{sale.stripe_code}", confirmation_url)

    def test_stripe_back_button(self):
        """Test stripe back button
        Expected: redirect to landing page
        """

        # Load stripe page
        self.load_stripe()

        # Click back button
        fields = self.get_selenium_elems(self.selectors)
        self.click_js_elem(fields["back_button"])

        # Validate redirect to landing page
        self.assertIn(settings.LANDING_HOST, self.driver.current_url)


class SaleDoneViewTestCase(TestApiViewsMethods, TestTravelsModelBase):
    """Test sale done view"""

    @classmethod
    def setUpTestData(cls):
        """Load fixtures only once"""
        call_command("apps_loaddata")
        call_command("load_pricing")

    def setUp(self):
        """Create sale with endpoint and setup tests data"""
        super().setUp(
            endpoint="/api/sales/done/", restricted_get=True, restricted_post=False
        )

        # Create initial sale with endpoint
        self.client_email = "john.doe@example.com"
        response = self.client.post(
            "/api/sales/",
            json.dumps(
                {
                    "service_type": 1,
                    "client_name": "John",
                    "client_email": self.client_email,
                    "location": 1,
                    "vehicle": 1,
                }
            ),
            content_type="application/json",
        )
        json_data = response.json()
        self.assertEqual(
            json_data["status"],
            "success",
            "Invalid response status when creating sale from endpoint",
        )

        # Get last sale from db
        self.sale = models.Sale.objects.all().last()

        # Api data
        self.data = {
            "sale_stripe_code": self.sale.stripe_code,
            "client_name": "Marco",
            "client_last_name": "Cabo",
            "client_phone": "4493402611",
            "passengers": 6,
            "details": "This is a test details",
        }

        self.arrival_data = {
            "arrival_date": "2025-01-01",
            "arrival_time": "10:00",
            "arrival_airline": "Airline",
            "arrival_flight_number": "1234567890",
        }

        self.departure_data = {
            "departure_date": "2025-01-01",
            "departure_time": "10:00",
            "departure_airline": "Airline",
            "departure_flight_number": "1234567890",
        }

    def test_post_missing_data(self):
        """Submit second part sale data, missing data
        Expected error: 400 response, sale no paid, sale no updated and no transfer created
        """

        # Get data and validate status code
        response = self.client.post(self.endpoint, {})
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        # Validate sale not paid
        self.sale.refresh_from_db()
        self.assertEqual(self.sale.paid, False)

        # Validate sale no updated
        self.assertNotEqual(self.sale.client.name, self.data["client_name"])
        self.assertNotEqual(self.sale.client.last_name, self.data["client_last_name"])
        self.assertNotEqual(self.sale.client.phone, self.data["client_phone"])
        self.assertNotEqual(self.sale.passengers, self.data["passengers"])
        self.assertNotEqual(self.sale.details, self.data["details"])

        # Valdiate no transfer created
        self.assertEqual(models.Transfer.objects.count(), 0)

    def test_post_missing_details(self):
        """SUbmit data only with mssing details.
        Expected ok: sale paid, sale updated, transfer created (details are optional)
        """
        
        self.data.update(self.arrival_data)
        self.data.pop("details")

        # Get data and validate status code
        response = self.client.post(self.endpoint, self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate sale paid
        self.sale.refresh_from_db()
        self.assertEqual(self.sale.paid, True)

        # Validate sale updated
        self.assertEqual(self.sale.client.name, self.data["client_name"])
        self.assertEqual(self.sale.client.last_name, self.data["client_last_name"])
        self.assertEqual(self.sale.client.phone, self.data["client_phone"])
        self.assertEqual(self.sale.passengers, self.data["passengers"])
        self.assertEqual(self.sale.details, None)

        # Validate transfer created
        self.assertEqual(models.Transfer.objects.count(), 1)
        transfer = models.Transfer.objects.get(sale=self.sale)
        self.assertEqual(
            transfer.date.strftime("%Y-%m-%d"), self.arrival_data["arrival_date"]
        )
        self.assertEqual(
            transfer.hour.strftime("%H:%M"), self.arrival_data["arrival_time"]
        )
        self.assertEqual(transfer.airline, self.arrival_data["arrival_airline"])
        self.assertEqual(
            transfer.flight_number, self.arrival_data["arrival_flight_number"]
        )

    def test_post_missing_arrival_data(self):
        """Submit second part sale data, missing arrival data
        Expected error: 400 response, sale no paid, sale no updated and no transfer created
        """

        # Get data and validate status code
        response = self.client.post(self.endpoint, self.data)
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        # Validate sale not paid
        self.sale.refresh_from_db()
        self.assertEqual(self.sale.paid, False)

        # Validate sale no updated
        self.assertNotEqual(self.sale.client.name, self.data["client_name"])
        self.assertNotEqual(self.sale.client.last_name, self.data["client_last_name"])
        self.assertNotEqual(self.sale.client.phone, self.data["client_phone"])
        self.assertNotEqual(self.sale.passengers, self.data["passengers"])
        self.assertNotEqual(self.sale.details, self.data["details"])

        # Valdiate no transfer created
        self.assertEqual(models.Transfer.objects.count(), 0)

    def test_post_arrival(self):
        """Submit second part sale data (only arrival data)
        Expected ok: sale paid, sale updated, transfer created
        """

        arriving_data = self.data.copy()
        arriving_data.update(self.arrival_data)

        # Get data and validate status code
        response = self.client.post(self.endpoint, arriving_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate sale paid
        self.sale.refresh_from_db()
        self.assertEqual(self.sale.paid, True)

        # Validate sale updated
        self.assertEqual(self.sale.client.name, self.data["client_name"])
        self.assertEqual(self.sale.client.last_name, self.data["client_last_name"])
        self.assertEqual(self.sale.client.phone, self.data["client_phone"])
        self.assertEqual(self.sale.passengers, self.data["passengers"])
        self.assertEqual(self.sale.details, self.data["details"])

        # Validate transfer created
        self.assertEqual(models.Transfer.objects.count(), 1)
        transfer = models.Transfer.objects.get(sale=self.sale)
        self.assertEqual(
            transfer.date.strftime("%Y-%m-%d"), self.arrival_data["arrival_date"]
        )
        self.assertEqual(
            transfer.hour.strftime("%H:%M"), self.arrival_data["arrival_time"]
        )
        self.assertEqual(transfer.airline, self.arrival_data["arrival_airline"])
        self.assertEqual(
            transfer.flight_number, self.arrival_data["arrival_flight_number"]
        )

    def test_post_departure(self):
        """Submit second part sale data (arrival and departure data)
        Expected ok: sale paid, sale updated, transfer created
        """

        # Update sale service type in db
        self.sale.service_type = models.ServiceType.objects.get(name="Round Trip")
        self.sale.save()

        departing_data = self.data.copy()
        departing_data.update(self.arrival_data)
        departing_data.update(self.departure_data)

        # Get data and validate status code
        response = self.client.post(self.endpoint, departing_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Validate sale paid
        self.sale.refresh_from_db()
        self.assertEqual(self.sale.paid, True)

        # Validate sale updated
        self.assertEqual(self.sale.client.name, self.data["client_name"])
        self.assertEqual(self.sale.client.last_name, self.data["client_last_name"])
        self.assertEqual(self.sale.client.phone, self.data["client_phone"])
        self.assertEqual(self.sale.passengers, self.data["passengers"])
        self.assertEqual(self.sale.details, self.data["details"])

        # Validate transfer created
        self.assertEqual(
            models.Transfer.objects.filter(sale=self.sale, type="arrival").count(), 1
        )
        transfer = models.Transfer.objects.get(sale=self.sale, type="arrival")
        self.assertEqual(
            transfer.date.strftime("%Y-%m-%d"), self.arrival_data["arrival_date"]
        )
        self.assertEqual(
            transfer.hour.strftime("%H:%M"), self.arrival_data["arrival_time"]
        )
        self.assertEqual(transfer.airline, self.arrival_data["arrival_airline"])
        self.assertEqual(
            transfer.flight_number, self.arrival_data["arrival_flight_number"]
        )

        # Validate departure transfer created
        self.assertEqual(
            models.Transfer.objects.filter(sale=self.sale, type="departure").count(), 1
        )
        transfer = models.Transfer.objects.get(sale=self.sale, type="departure")
        self.assertEqual(
            transfer.date.strftime("%Y-%m-%d"), self.departure_data["departure_date"]
        )
        self.assertEqual(
            transfer.hour.strftime("%H:%M"), self.departure_data["departure_time"]
        )
        self.assertEqual(transfer.airline, self.departure_data["departure_airline"])
        self.assertEqual(
            transfer.flight_number, self.departure_data["departure_flight_number"]
        )

    def test_post_invalid_stripe_code(self):
        """Test get sale done with invalid stripe code
        Expected: error redirect
        """

        # Change stripe code in data
        self.data["sale_stripe_code"] = "invalid"
        self.data.update(self.arrival_data)

        # Get data and validate status code
        response = self.client.post(self.endpoint, self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Validate error
        response_json = response.json()
        self.assertEqual(response_json["status"], "error")
        self.assertEqual(response_json["message"], "Invalid sale data")
        self.assertEqual(response_json["status"], "error")
        self.assertEqual(response_json["message"], "Invalid sale data")

        # Validate no sale updated
        self.sale.refresh_from_db()
        self.assertEqual(self.sale.paid, False)
        self.assertNotEqual(self.sale.client.name, self.data["client_name"])
        self.assertNotEqual(self.sale.client.last_name, self.data["client_last_name"])
        self.assertNotEqual(self.sale.client.phone, self.data["client_phone"])
        self.assertNotEqual(self.sale.passengers, self.data["passengers"])
        self.assertNotEqual(self.sale.details, self.data["details"])

        # Valdiate no transfer created
        self.assertEqual(models.Transfer.objects.count(), 0)

    def test_post_sale_already_paid(self):
        """Test get sale done with sale already paid
        Expected: error redirect
        """

        # Formatd ata
        self.data.update(self.arrival_data)

        response = self.client.post(self.endpoint, self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Submit form again
        response = self.client.post(self.endpoint, self.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Validate error
        response_json = response.json()
        self.assertEqual(response_json["status"], "error")
        self.assertEqual(response_json["message"], "Sale already paid")