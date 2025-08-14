from time import sleep

from django.test import LiveServerTestCase
from django.conf import settings
from django.contrib.auth.models import User

from rest_framework.test import APITestCase
from rest_framework import status

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By


class TestApiViewsMethods(APITestCase):
    """Base class for testing api views that only allows get views"""

    def setUp(
        self,
        endpoint="/api/",
        restricted_get: bool = False,
        restricted_post: bool = True,
        restricted_put: bool = True,
        restricted_patch: bool = True,
        restricted_delete: bool = True,
    ):
        """Initialize test data

        restricted_get (bool): If the get method is restricted
        restricted_post (bool): If the post method is restricted
        restricted_put (bool): If the put method is restricted
        restricted_delete (bool): If the delete method is restricted
        """

        # Create user and login
        username = "test_user"
        password = "test_pass"
        User.objects.create_superuser(
            username=username,
            email="test@gmail.com",
            password=password,
        )
        self.client.login(username=username, password=password)

        # Save data
        self.endpoint = endpoint
        self.restricted_get = restricted_get
        self.restricted_post = restricted_post
        self.restricted_put = restricted_put
        self.restricted_patch = restricted_patch
        self.restricted_delete = restricted_delete

    def validate_invalid_method(self, method: str):
        """Validate that the given method is not allowed on the endpoint"""

        response = getattr(self.client, method)(self.endpoint)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_authenticated_user_post(self):
        """Test that authenticated users can not post to the endpoint"""

        if self.restricted_post:
            self.validate_invalid_method("post")

    def test_authenticated_user_put(self):
        """Test that authenticated users can not put to the endpoint"""

        if self.restricted_put:
            self.validate_invalid_method("put")

    def test_authenticated_user_patch(self):
        """Test that authenticated users can not patch to the endpoint"""

        if self.restricted_patch:
            self.validate_invalid_method("patch")

    def test_authenticated_user_delete(self):
        """Test that authenticated users can not delete to the endpoint"""

        if self.restricted_delete:
            self.validate_invalid_method("delete")

    def test_authenticated_user_get(self):
        """Test that authenticated users can get to the endpoint"""

        if self.restricted_get:
            self.validate_invalid_method("get")

    def test_unauthenticated_user_get(self):
        """Test unauthenticated user get request"""

        # Remove authentication
        self.client.logout()

        # Make request
        response = self.client.get(self.endpoint)

        # Check response
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestSeleniumBase(LiveServerTestCase):
    """Base class to test admin with selenium (login and setup)"""

    def setUp(self, endpoint="/"):
        """Load data, setup and login in each test"""

        # Setup selenium
        self.endpoint = endpoint
        self.__setup_selenium__()

    def tearDown(self):
        """Close selenium"""
        try:
            self.driver.quit()
        except Exception:
            pass

    def __setup_selenium__(self):
        """Setup and open selenium browser"""
        chrome_options = Options()

        # Run in headless mode if enabled
        if settings.TEST_HEADLESS:
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--disable-gpu")

        # Allow clipboard access
        prefs = {"profile.default_content_setting_values.clipboard": 1}
        chrome_options.add_experimental_option("prefs", prefs)

        # Disable Chrome automation infobars and password save popups
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(5)

    def set_page(self, endpoint):
        """Set page"""
        self.driver.get(f"{self.live_server_url}{endpoint}")
        sleep(2)

    def get_selenium_elems(self, selectors: dict) -> dict[str, WebElement]:
        """Get selenium elements from selectors

        Args:
            selectors (dict): css selectors to find: name, value

        Returns:
            dict[str, WebElement]: selenium elements: name, value
        """
        fields = {}
        for key, value in selectors.items():
            try:
                fields[key] = self.driver.find_element(By.CSS_SELECTOR, value)
            except Exception:
                fields[key] = None
        return fields
    
    def click_js_elem(self, element: WebElement):
        """Click element with javascript"""
        self.driver.execute_script("arguments[0].click();", element)
