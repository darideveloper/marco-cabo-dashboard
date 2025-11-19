import os
import csv

from django.core.management.base import BaseCommand

from travels import models


BASE_FILE = os.path.basename(__file__)


class Command(BaseCommand):
    help = "Load pricing data from local csv file"

    def clean_price(self, price: str) -> float:
        return float(price.replace("$", "").replace(",", "").strip())

    def handle(self, *args, **kwargs):
        
        # Delete old pricing
        models.Pricing.objects.all().delete()

        # Get DB models
        suburban = models.Vehicle.objects.get(name="Luxury SUV")
        van = models.Vehicle.objects.get(name="Executive Van")
        sprinter = models.Vehicle.objects.get(name="Sprinter")
        oneway = models.ServiceType.objects.get(name="One Way")
        roundtrip = models.ServiceType.objects.get(name="Round Trip")

        # Read excel
        csv_path = os.path.join(os.path.dirname(__file__), "pricing.csv")
        with open(csv_path, "r") as csv_file:
            csv_reader = csv.reader(csv_file)

            # Get data from row
            for row in list(csv_reader)[2:]:
                (
                    zone_str,
                    location_str,
                    suburban_oneway_price,
                    van_oneway_price,
                    sprinter_oneway_price,
                    _,
                    suburban_roundtrip_price,
                    van_roundtrip_price,
                    sprinter_roundtrip_price,
                ) = row
                zone_str = zone_str.replace("-", "").strip()
                location_str = location_str.strip()
                suburban_oneway_price = self.clean_price(suburban_oneway_price)
                van_oneway_price = self.clean_price(van_oneway_price)
                sprinter_oneway_price = self.clean_price(sprinter_oneway_price)
                suburban_roundtrip_price = self.clean_price(
                    suburban_roundtrip_price
                )
                van_roundtrip_price = self.clean_price(van_roundtrip_price)
                sprinter_roundtrip_price = self.clean_price(
                    sprinter_roundtrip_price
                )
                
                print(f"Saving pricing for {zone_str} - {location_str}")
                
                # Get row models
                zone = models.Zone.objects.get(name=zone_str)
                location = models.Location.objects.get(name=location_str, zone=zone)

                # Create one way pricing
                models.Pricing.objects.create(
                    location=location,
                    vehicle=suburban,
                    service_type=oneway,
                    price=suburban_oneway_price,
                )
                
                models.Pricing.objects.create(
                    location=location,
                    vehicle=van,
                    service_type=oneway,
                    price=van_oneway_price,
                )
                
                models.Pricing.objects.create(
                    location=location,
                    vehicle=sprinter,
                    service_type=oneway,
                    price=sprinter_oneway_price,
                )
                
                # Create round trip pricing
                models.Pricing.objects.create(
                    location=location,
                    vehicle=suburban,
                    service_type=roundtrip,
                    price=suburban_roundtrip_price,
                )
                
                models.Pricing.objects.create(
                    location=location,
                    vehicle=van,
                    service_type=roundtrip,
                    price=van_roundtrip_price,
                )
                
                models.Pricing.objects.create(
                    location=location,
                    vehicle=sprinter,
                    service_type=roundtrip,
                    price=sprinter_roundtrip_price,
                )