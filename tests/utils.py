import json
import os
import ssl
import subprocess
import time
from time import sleep

import docker
from openwisp_utils.tests import SeleniumTestMixin
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.common.by import By


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


class TestUtilities(SeleniumTestMixin, TestConfig):
    """Utility functions for testing."""

    objects_to_delete = []
    browser = 'chrome'

    def setUp(self):
        # Override TestSeleniumMixin setUp which uses
        # Django methods to create superuser
        return

    def login(self, username=None, password=None, driver=None):
        super().login(username, password, driver)
        # Workaround for JS logic in chart-utils.js
        # which fails to perform a XHR request
        # during automated tests, it seems that the
        # lack of pause causes the request to fail randomly
        sleep(0.5)

    def _ignore_location_alert(self, driver=None):
        """Accept alerts related to location not found.

        Parameters:

        - driver (selenium.webdriver, optional): The Selenium WebDriver
          instance. Defaults to `self.base_driver`.
        """
        expected_msg = 'Could not find any address related to this location.'
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
        # Scroll to the top of the page. This will ensure that the save
        # button is visible and clickable.
        driver.execute_script('window.scrollTo(0, 0);')
        self.find_element(By.NAME, '_save', driver=driver).click()

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
        self.open('/admin/openwisp_users/user/add/', driver=driver)
        self.find_element(By.NAME, 'username', driver=driver).send_keys(username)
        self.find_element(By.NAME, 'email', driver=driver).send_keys(email)
        self.find_element(By.NAME, 'password1', driver=driver).send_keys(password)
        self.find_element(By.NAME, 'password2', driver=driver).send_keys(password)
        self.find_element(By.NAME, 'is_superuser', driver=driver).click()
        self._click_save_btn(driver)
        self.objects_to_delete.append(driver.current_url)
        self._click_save_btn(driver)
        self._wait_until_page_ready()
        self.wait_for_visibility(By.ID, 'content', driver=driver, timeout=10)

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
        self.open(path, driver=driver)
        resources = self.find_elements(
            By.CLASS_NAME, select_field, wait_for='presence', driver=driver
        )
        for resource in resources:
            if len(resource.find_elements(By.LINK_TEXT, resource_name)):
                resource.find_element(By.LINK_TEXT, resource_name).click()
                break
        self._wait_until_page_ready()

    def select_resource(self, name, driver=None):
        """Select a resource by name.

        Parameters:

        - name (str): The name of the resource to select.
        - driver (selenium.webdriver, optional): The Selenium WebDriver
          instance. Defaults to `self.base_driver`.
        """
        if not driver:
            driver = self.base_driver
        path = f'//a[contains(text(), "{name}")]/../..//input[@name="_selected_action"]'
        self.find_element(By.XPATH, path, driver=driver).click()

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
        self.open(path, driver=driver)
        self.select_resource(name)
        self.find_element(By.NAME, 'action', driver=driver).find_element(
            By.XPATH,
            f'//option[@value="{option}"]',
        ).click()
        self.find_element(By.NAME, 'index', driver=driver).click()

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
        logs = self.get_browser_logs(driver=driver)
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
        self.open('/admin/geo/location/add/', driver=driver)
        self.find_element(By.NAME, 'organization', driver=driver).find_element(
            By.XPATH, '//option[text()="default"]'
        ).click()
        self.find_element(By.NAME, 'name', driver=driver).send_keys(location_name)
        self.find_element(By.NAME, 'type', driver=driver).find_element(
            By.XPATH, '//option[@value="outdoor"]'
        ).click()
        self.find_element(By.NAME, 'is_mobile', driver=driver).click()
        self._ignore_location_alert(driver)
        self._click_save_btn(driver)
        self.get_resource(location_name, '/admin/geo/location/', driver=driver)
        self._wait_until_page_ready()
        self.objects_to_delete.append(driver.current_url)
        self.open('/admin/geo/location/', driver=driver)
        self._wait_until_page_ready()

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
        self.find_element(By.NAME, 'is_mobile', driver=driver).click()
        self._ignore_location_alert(driver)
        self.find_element(
            By.CLASS_NAME, 'leaflet-draw-draw-marker', driver=driver
        ).click()
        self.find_element(By.ID, 'id_geometry-map', driver=driver).click()
        self.find_element(By.NAME, 'is_mobile', driver=driver).click()
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
        self.open('/admin/topology/topology/add/', driver=driver)
        self.find_element(By.NAME, 'label', driver=driver).send_keys(label)
        # We can leave the organization empty for creating shared object
        self.find_element(By.NAME, 'parser', driver=driver).find_element(
            By.XPATH, '//option[text()="NetJSON NetworkGraph"]'
        ).click()
        self.find_element(By.NAME, 'url', driver=driver).send_keys(topology_url)
        self._click_save_btn(driver)
        self.get_resource(
            label, '/admin/topology/topology/', 'field-label', driver=driver
        )
        self._wait_until_page_ready()
        self.objects_to_delete.append(driver.current_url)
        self._wait_until_page_ready()
