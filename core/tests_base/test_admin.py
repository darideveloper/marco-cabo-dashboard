from time import sleep

from django.contrib.auth.models import User
from django.test import TestCase

from core.tests_base.test_views import TestSeleniumBase


class TestAdminBase(TestCase):
    """ Base class to test admin """
    
    def setUp(self):
        """ Load data and create admin user """
        
        # Load data
        # call_command("apps_loaddata")
        
        # Create admin user
        self.admin_user, self.admin_pass, self.admin = self.create_admin_user()
        
        # Login in client
        self.client.login(username=self.admin_user, password=self.admin_pass)
    
    def create_admin_user(self) -> tuple[str, str, User]:
        """ Create a new admin user and return it
        
        Returns:
            tuple:
                str: Username of the user created
                str: Password of the user created
                User: User created
        """
        
        # Create admin user
        password = "admin"
        user = User.objects.create_superuser(
            username="admin",
            email="test@gmail.com",
            password=password,
        )
        
        return user.username, password, user
    
    def submit_search_bar(self, endpoint: str, search_text: str = "test"):
        """ Validate search bar in admin page
        
        Args:
            endpoint (str): Endpoint to test inside /admin/
            search_text (str): Text to search. Defaults to "test".
        """
        
        # Fix endpoint prefix if needed
        if not endpoint.startswith("/admin/"):
            endpoint = f"/admin/{endpoint.lstrip('/')}"
        
        # Get response
        response = self.client.get(f"{endpoint}", {"q": search_text})
        print(f"Testing search bar in {endpoint} with text '{search_text}'")
        
        # Check if the response is valid
        self.assertEqual(response.status_code, 200)
        
        # Check if the search text is in the response content
        self.assertContains(response, search_text)


class TestAdminSeleniumBase(TestAdminBase, TestSeleniumBase):
    """ Base class to test admin with selenium (login and setup) """
    
    def setUp(self, endpoint="/admin/"):
        """ Load data, setup and login in each test """
        
        # Load data
        # call_command("apps_loaddata")
        
        # Create admin user
        self.admin_user, self.admin_pass, self.admin = self.create_admin_user()
        
        # Setup selenium
        super().setUp()
        self.endpoint = endpoint
        
        # Login in admin when selenium is ready
        self.__login__()

    def __login__(self):
        
        # Load login page and get fields
        self.driver.get(f"{self.live_server_url}/admin/")
        sleep(2)
        selectors_login = {
            "username": "input[name='username']",
            "password": "input[name='password']",
            "submit": "button[type='submit']",
        }
        fields_login = self.get_selenium_elems(selectors_login)

        fields_login["username"].send_keys(self.admin_user)
        fields_login["password"].send_keys(self.admin_pass)
        fields_login["submit"].click()

        # Wait after login
        sleep(3)
        
        # Open page
        self.driver.get(f"{self.live_server_url}{self.endpoint}")
        sleep(2)