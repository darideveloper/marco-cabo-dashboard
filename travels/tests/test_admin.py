from core.tests_base.test_admin import TestAdminBase


class ClientAdminTestCase(TestAdminBase):
    """Testing client admin"""

    def setUp(self):
        super().setUp()
        self.endpoint = "/admin/travels/client/"

    def test_search_bar(self):
        """Validate search bar working"""

        self.submit_search_bar(self.endpoint)


class CodeAdminTestCase(TestAdminBase):
    """Testing code admin"""

    def setUp(self):
        super().setUp()
        self.endpoint = "/admin/travels/code/"

    def test_search_bar(self):
        """Validate search bar working"""

        self.submit_search_bar(self.endpoint)


class SaleAdminTestCase(TestAdminBase):
    """Testing sale admin"""

    def setUp(self):
        super().setUp()
        self.endpoint = "/admin/travels/sale/"

    def test_search_bar(self):
        """Validate search bar working"""

        self.submit_search_bar(self.endpoint)


class TransferAdminTestCase(TestAdminBase):
    """Testing transfer admin"""

    def setUp(self):
        super().setUp()
        self.endpoint = "/admin/travels/transfer/"

    def test_search_bar(self):
        """Validate search bar working"""

        self.submit_search_bar(self.endpoint)
