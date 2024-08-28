import json
import os
import ssl
import subprocess
import time

import docker
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class TestConfig:
    """Configuration class for setting up test parameters and utilities."""

    def shortDescription(self):
        """Return a short description for the test."""
        return None

    docker_client = docker.from_env()
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    config_file = os.path.join(os.path.dirname(__file__), 'config.json')
    root_location = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
    with open(config_file) as json_file:
        config = json.load(json_file)


class TestUtilities(TestConfig):
    """Utility functions for testing."""

    objects_to_delete = []

    def login(self, username=None, password=None, driver=None):
        """Log in to the admin dashboard.

        Parameters:

        - username (str, optional): The username to use for login.
          Defaults to the value in the config.
        - password (str, optional): The password to use for login.
          Defaults to the value in the config.
        - driver (selenium.webdriver, optional): The Selenium WebDriver
          instance. Defaults to `self.base_driver`.
        """
        if not driver:
            driver = self.base_driver
        if not username:
            username = self.config['username']
        if not password:
            password = self.config['password']
        driver.get(f"{self.config['app_url']}/admin/login/")
        if 'admin/login' in driver.current_url:
            driver.find_element(By.NAME, 'username').send_keys(username)
            driver.find_element(By.NAME, 'password').send_keys(password)
            driver.find_element(By.XPATH, "//input[@type='submit']").click()

    def _ignore_location_alert(self, driver=None):
        """Accept alerts related to location not found.

        Parameters:

        - driver (selenium.webdriver, optional): The Selenium WebDriver
          instance. Defaults to `self.base_driver`.
        """
        expected_msg = "Could not find any address related to this location."
        if not driver:
            driver = self.base_driver
        time.sleep(2)  # Wait for the alert to appear
        try:
            window_alert = driver.switch_to.alert
            if expected_msg in window_alert.text:
                window_alert.accept()
        except NoAlertPresentException:
            pass  # No alert is okay.

    def _click_save_btn(self, driver=None):
        """Click the save button in the admin interface.

        Parameters:

        - driver (selenium.webdriver, optional): The Selenium WebDriver
          instance. Defaults to `self.base_driver`.
        """
        if not driver:
            driver = self.base_driver
        save_btn = driver.find_element(By.NAME, '_save')
        actions = ActionChains(driver)
        actions.move_to_element(save_btn).click().perform()

    def create_superuser(
        self,
        email='test@user.com',
        username='test_superuser',
        password='randomPassword01!',
        driver=None,
    ):
        """Create a new superuser.

        Parameters:

        - email (str, optional): The email address of the superuser.
          Defaults to 'test@user.com'.
        - username (str, optional): The username of the superuser.
          Defaults to 'test_superuser'.
        - password (str, optional): The password for the superuser.
          Defaults to 'randomPassword01!'.
        - driver (selenium.webdriver, optional): The Selenium WebDriver
          instance. Defaults to `self.base_driver`.
        """
        if not driver:
            driver = self.base_driver
        driver.get(f"{self.config['app_url']}/admin/openwisp_users/user/add/")
        self._wait_for_element()
        driver.find_element(By.NAME, 'username').send_keys(username)
        driver.find_element(By.NAME, 'email').send_keys(email)
        driver.find_element(By.NAME, 'password1').send_keys(password)
        driver.find_element(By.NAME, 'password2').send_keys(password)
        driver.find_element(By.NAME, 'is_superuser').click()
        self._click_save_btn(driver)
        self.objects_to_delete.append(driver.current_url)
        self._click_save_btn(driver)
        self._wait_for_element()

    def get_resource(self, resource_name, path, select_field='field-name', driver=None):
        """Navigate to a resource's change form page.

        Parameters:

        - resource_name (str): The name of the resource to find.
        - path (str): The path to the resource in the admin interface.
        - select_field (str, optional): The field used to identify the
          resource. Defaults to 'field-name'.
        - driver (selenium.webdriver, optional): The Selenium WebDriver
          instance. Defaults to `self.base_driver`.
        """
        if not driver:
            driver = self.base_driver
        driver.get(f"{self.config['app_url']}{path}")
        resources = driver.find_elements(By.CLASS_NAME, select_field)
        for resource in resources:
            if len(resource.find_elements(By.LINK_TEXT, resource_name)):
                resource.find_element(By.LINK_TEXT, resource_name).click()
                break

    def select_resource(self, name, driver=None):
        """Select a resource by name.

        Parameters:

        - name (str): The name of the resource to select.
        - driver (selenium.webdriver, optional): The Selenium WebDriver
          instance. Defaults to `self.base_driver`.
        """
        if not driver:
            driver = self.base_driver
        path = (
            f'//a[contains(text(), "{name}")]/../../' '/input[@name="_selected_action"]'
        )
        driver.find_element(By.XPATH, path).click()

    def action_on_resource(self, name, path, option, driver=None):
        """Perform an action on a resource.

        Parameters:

        - name (str): The name of the resource to select.
        - path (str): The path to the resource list page.
        - option (str): The value of the option to select.
        - driver (selenium.webdriver, optional): The Selenium WebDriver
          instance. Defaults to `self.base_driver`.
        """
        if not driver:
            driver = self.base_driver
        driver.get(f"{self.config['app_url']}{path}")
        self.select_resource(name)
        driver.find_element(By.NAME, 'action').find_element(
            By.XPATH, f'//option[@value="{option}"]'
        ).click()
        driver.find_element(By.NAME, 'index').click()

    def console_error_check(self, driver=None):
        """Check for JavaScript errors in the console.

        Parameters:

        - driver (selenium.webdriver, optional): The Selenium WebDriver
          instance. Defaults to `self.base_driver`.

        Returns:
            list: A list of JavaScript error messages.
        """
        if not driver:
            driver = self.base_driver
        console_logs = []
        if self.config['driver'] == 'chromium':
            logs = driver.get_log('browser')
            for logentry in logs:
                if logentry['level'] == 'SEVERE':
                    # Ignore error generated due to "leaflet" issue
                    # https://github.com/makinacorpus/django-leaflet/pull/380
                    if 'leaflet' in logentry['message']:
                        continue
                    # Ignore error generated due to "beforeunload" chrome issue
                    # https://stackoverflow.com/questions/10680544/beforeunload-chrome-issue
                    if 'beforeunload' in logentry['message']:
                        continue
                    console_logs.append(logentry['message'])
        return console_logs

    def create_mobile_location(self, location_name, driver=None):
        """Create a new mobile location.

        Parameters:

        - location_name (str): The name of the new location.
        - driver (selenium.webdriver, optional): The Selenium WebDriver
          instance. Defaults to `self.base_driver`.
        """
        if not driver:
            driver = self.base_driver
        driver.get(f"{self.config['app_url']}/admin/geo/location/add/")
        driver.find_element(By.NAME, 'organization').find_element(
            By.XPATH, '//option[text()="default"]'
        ).click()
        driver.find_element(By.NAME, 'name').send_keys(location_name)
        driver.find_element(By.NAME, 'type').find_element(
            By.XPATH, '//option[@value="outdoor"]'
        ).click()
        driver.find_element(By.NAME, 'is_mobile').click()
        self._ignore_location_alert(driver)
        self._click_save_btn(driver)
        self.get_resource(location_name, '/admin/geo/location/', driver=driver)
        self._wait_for_element()
        self.objects_to_delete.append(driver.current_url)
        driver.get(f"{self.config['app_url']}/admin/geo/location/")
        self._wait_for_element()

    def add_mobile_location_point(self, location_name, driver=None):
        """Add a point on the map for an existing mobile location.

        Parameters:

        - location_name (str): The name of the location.
        - driver (selenium.webdriver, optional): The Selenium WebDriver
          instance. Defaults to `self.base_driver`.
        """
        if not driver:
            driver = self.base_driver
        self.get_resource(location_name, '/admin/geo/location/', driver=driver)
        driver.find_element(By.NAME, 'is_mobile').click()
        self._ignore_location_alert(driver)
        driver.find_element(By.CLASS_NAME, 'leaflet-draw-draw-marker').click()
        driver.find_element(By.ID, 'id_geometry-map').click()
        driver.find_element(By.NAME, 'is_mobile').click()
        self._ignore_location_alert(driver)
        self._click_save_btn(driver)
        self.get_resource(location_name, '/admin/geo/location/', driver=driver)

    def docker_compose_get_container_id(self, container_name):
        """Get the Docker container ID for a specific container.

        Parameters:

        - container_name (str): The name of the Docker container.

        Returns:
            str: The ID of the Docker container.
        """
        services_output = subprocess.Popen(
            ['docker', 'compose', 'ps', '--quiet', container_name],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.root_location,
        )
        output, _ = services_output.communicate()
        return output.rstrip().decode('utf-8')

    def create_network_topology(
        self,
        label='automated-selenium-test-01',
        topology_url=(
            'https://raw.githubusercontent.com/openwisp/'
            'docker-openwisp/master/tests/static/network-graph.json'
        ),
        driver=None,
    ):
        """Create a new network topology resource.

        Parameters:

        - label (str, optional): The label for the new topology. Defaults
          to 'automated-selenium-test-01'.
        - topology_url (str, optional): The URL to fetch the topology data
          from. Defaults to the provided URL.
        - driver (selenium.webdriver, optional): The Selenium WebDriver
          instance. Defaults to `self.base_driver`.
        """
        if not driver:
            driver = self.base_driver
        driver.get(f"{self.config['app_url']}/admin/topology/topology/add/")
        driver.find_element(By.NAME, 'label').send_keys(label)
        driver.find_element(
            by=By.CSS_SELECTOR, value='#select2-id_organization-container'
        ).click()
        driver.find_element(By.NAME, 'parser').find_element(
            By.XPATH, '//option[text()="NetJSON NetworkGraph"]'
        ).click()
        driver.find_element(By.NAME, 'url').send_keys(topology_url)
        self._click_save_btn(driver)
        self.get_resource(
            label, '/admin/topology/topology/', 'field-label', driver=driver
        )
        self._wait_for_element()
        self.objects_to_delete.append(driver.current_url)
        driver.get(f"{self.config['app_url']}/admin/topology/topology/")
        self._wait_for_element()

    def _wait_for_element(self, element_id='content'):
        """Wait for an element to be visible on the page.

        Parameters:

        - element_id (str, optional): The ID of the element to wait for.
          Defaults to 'content'.
        """
        WebDriverWait(self.base_driver, 10).until(
            EC.visibility_of_element_located((By.ID, element_id))
        )
