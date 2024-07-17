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
    """
    Get the configurations that are to be used for all the tests.
    """

    def shortDescription(self):
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
    """
    Utility functions that are used during testing.
    """

    objects_to_delete = []

    def login(self, username=None, password=None, driver=None):
        """
        Log in to the admin dashboard
        Argument:
            driver: selenium driver (default: cls.base_driver)
            username: username to be used for login (default: cls.config['username'])
            password: password to be used for login (default: cls.config['password'])
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
        """
        Accepts related address to location not found alert
        Argument:
            driver: selenium driver (default: cls.base_driver)
        """
        expectedMsg = "Could not find any address related to this location."
        if not driver:
            driver = self.base_driver
        time.sleep(2)  # Wait for two seconds for alert to come up
        try:
            windowAlert = driver.switch_to.alert
            if expectedMsg in windowAlert.text:
                windowAlert.accept()
        except NoAlertPresentException:
            pass  # No alert is okay.

    def _click_save_btn(self, driver=None):
        saveBtn = driver.find_element(By.NAME, '_save')
        actions = ActionChains(driver)
        actions.move_to_element(saveBtn).click().perform()

    def create_superuser(
        self,
        email='test@user.com',
        username='test_superuser',
        password='randomPassword01!',
        driver=None,
    ):
        """
        Create new superuser
        Argument:
            email: password for user (default: randomPassword01!)
            username: username for user (default: test_superuser)
            password: password for user (default: randomPassword01!)
            driver: selenium driver (default: cls.base_driver)
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
        """
        Redirect to resource's change form page.
        Argument:
            resource_name: username of user to use for operation (example: 'users')
            path: path to the resource. (example: '/admin/openwisp_users/user/')
            select_field: field used to select the resource. (default: 'field-name')
            driver: selenium driver (default: cls.base_driver)
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
        """
        Select checkbox of a resource with resource name.
        Argument:
            name: name of the resource to select
            driver: selenium driver (default: cls.base_driver)
        """
        if not driver:
            driver = self.base_driver
        path = (
            f'//a[contains(text(), "{name}")]/../../' '/input[@name="_selected_action"]'
        )
        driver.find_element(By.XPATH, path).click()

    def action_on_resource(self, name, path, option, driver=None):
        """
        Perform action on resource:
        Arguement:
            name: name of the resource to select
            path: path to reach the list page
            option: value of option to be deleted
            driver: selenium driver (default: cls.base_driver)
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
        """
        Return all js errors that occured
        Firefox doesn't support it yet, read here:
        https://github.com/mozilla/geckodriver/issues/284
        Argument:
            driver: selenium driver (default: cls.base_driver)
        """
        if not driver:
            driver = self.base_driver
        console_logs = []
        if self.config['driver'] == 'chromium':
            logs = driver.get_log('browser')
            for logentry in logs:
                if logentry['level'] in ['SEVERE']:
                    console_logs.append(logentry['message'])
        return console_logs

    def create_mobile_location(self, location_name, driver=None):
        """
        Create a new location with `location_name`
        Argument:
            location_name: location to use for operation
            driver: selenium driver (default: cls.base_driver)
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
        # Add to delete list
        self.get_resource(location_name, '/admin/geo/location/', driver=driver)
        self._wait_for_element()
        self.objects_to_delete.append(driver.current_url)
        driver.get(f"{self.config['app_url']}/admin/geo/location/")
        self._wait_for_element()

    def add_mobile_location_point(self, location_name, driver=None):
        """
        Adds a point on map for an existing mobile location.
        Argument:
            location_name: location to use for operation
            driver: selenium driver (default: cls.base_driver)
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
        """
        Create a new fetch type network-toplogy resource.
        Argument:
            topology_url: fetch link of the topology
            label: name of the topology (default: 'default')
            location_name: location to use for operation
            driver: selenium driver (default: cls.base_driver)
        """
        if not driver:
            driver = self.base_driver
        driver.get(f"{self.config['app_url']}/admin/topology/topology/add/")
        driver.find_element(By.NAME, 'label').send_keys(label)
        # We have to select the organisation field from the
        # autocomplete filter of openwisp-network-topology
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
        WebDriverWait(self.base_driver, 10).until(
            EC.visibility_of_element_located((By.ID, element_id))
        )
