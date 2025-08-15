from core.tests_base.test_admin import TestAdminBase


class ClientAdminTestCase(TestAdminBase):
    """Testing client admin"""

    def setUp(self):
        super().setUp()
        self.endpoint = "/admin/travels/client/"

    def test_search_bar(self):
        """Validate search bar working"""

        self.submit_search_bar(self.endpoint)


class VipCodeAdminTestCase(TestAdminBase):
    """Testing code admin"""

    def setUp(self):
        super().setUp()
        self.endpoint = "/admin/travels/vipcode/"

    def test_search_bar(self):
        """Validate search bar working"""

        self.submit_search_bar(self.endpoint)


class VehicleAdminTestCase(TestAdminBase):
    """Testing vehicle admin"""

    def setUp(self):
        super().setUp()
        self.endpoint = "/admin/travels/vehicle/"


class SaleAdminTestCase(TestAdminBase):
    """Testing sale admin"""

    def setUp(self):
        super().setUp()
        self.endpoint = "/admin/travels/sale/"

    def test_search_bar(self):
        """Validate search bar working"""

        self.submit_search_bar(self.endpoint)
        
    def test_custom_links(self):
        """Validate custom custom links"""

        links = {
            "Transportaciones": "/admin/travels/transfer/",
        }

        # Open employee list page
        response = self.client.get("/admin/travels/sale/")

        # Validate links
        for link_text, link in links.items():
            self.assertContains(response, link_text)
            self.assertContains(response, link)


class ServiceTypeAdminTestCase(TestAdminBase):
    """Testing transfer type admin"""

    def setUp(self):
        super().setUp()
        self.endpoint = "/admin/travels/servicetype/"


class TransferAdminTestCase(TestAdminBase):
    """Testing transfer admin"""

    def setUp(self):
        super().setUp()
        self.endpoint = "/admin/travels/transfer/"

    def test_search_bar(self):
        """Validate search bar working"""

        self.submit_search_bar(self.endpoint)


class ZoneAdminTestCase(TestAdminBase):
    """Testing zone admin"""

    def setUp(self):
        super().setUp()
        self.endpoint = "/admin/travels/zone/"

    def test_search_bar(self):
        """Validate search bar working"""

        self.submit_search_bar(self.endpoint)


class LocationAdminTestCase(TestAdminBase):
    """Testing location admin"""

    def setUp(self):
        super().setUp()
        self.endpoint = "/admin/travels/location/"

    def test_search_bar(self):
        """Validate search bar working"""

        self.submit_search_bar(self.endpoint)


class PricingAdminTestCase(TestAdminBase):
    """Testing pricing admin"""

    def setUp(self):
        super().setUp()
        self.endpoint = "/admin/travels/pricing/"

    def test_search_bar(self):
        """Validate search bar working"""

        self.submit_search_bar(self.endpoint)