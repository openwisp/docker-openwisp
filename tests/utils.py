import json
import os


class TestConfig(object):
    """
    Get the configurations that are to be used for all the tests.
    """

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
            driver.find_element_by_name('username').send_keys(username)
            driver.find_element_by_name('password').send_keys(password)
            driver.find_element_by_xpath("//input[@type='submit']").click()

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
        driver.find_element_by_name('username').send_keys(username)
        driver.find_element_by_name('email').send_keys(email)
        driver.find_element_by_name('password1').send_keys(password)
        driver.find_element_by_name('password2').send_keys(password)
        driver.find_element_by_name('is_superuser').click()
        driver.find_element_by_name('_save').click()
        self.objects_to_delete.append(driver.current_url)
        driver.find_element_by_name('_save').click()

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
        resources = driver.find_elements_by_class_name(select_field)
        for resource in resources:
            if len(resource.find_elements_by_link_text(resource_name)):
                resource.find_element_by_link_text(resource_name).click()
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
        driver.find_element_by_xpath(path).click()

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
        driver.find_element_by_name('action').find_element_by_xpath(
            f'//option[@value="{option}"]'
        ).click()
        driver.find_element_by_name('index').click()

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
        driver.find_element_by_name('organization').find_element_by_xpath(
            '//option[text()="default"]'
        ).click()
        driver.find_element_by_name('name').send_keys(location_name)
        driver.find_element_by_name('type').find_element_by_xpath(
            '//option[@value="outdoor"]'
        ).click()
        driver.find_element_by_name('is_mobile').click()
        driver.find_element_by_name('_save').click()
        # Add to delete list
        self.get_resource(location_name, '/admin/geo/location/', driver=driver)
        self.objects_to_delete.append(driver.current_url)
        driver.get(f"{self.config['app_url']}/admin/geo/location/")

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
        driver.find_element_by_name('is_mobile').click()
        driver.find_element_by_class_name('leaflet-draw-draw-marker').click()
        driver.find_element_by_id('id_geometry-map').click()
        driver.find_element_by_name('is_mobile').click()
        driver.find_element_by_name('_save').click()
        self.get_resource(location_name, '/admin/geo/location/', driver=driver)

    def create_network_topology(
        self,
        label='automated-selenium-test-01',
        topology_url='https://pastebin.com/raw/ZMHRRYss',
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
        driver.find_element_by_name('label').send_keys(label)
        driver.find_element_by_name('organization').find_element_by_xpath(
            '//option[text()="default"]'
        ).click()
        driver.find_element_by_name('parser').find_element_by_xpath(
            '//option[text()="NetJSON NetworkGraph"]'
        ).click()
        driver.find_element_by_name('url').send_keys(topology_url)
        driver.find_element_by_name('_save').click()
        self.get_resource(
            label, '/admin/topology/topology/', 'field-label', driver=driver
        )
        self.objects_to_delete.append(driver.current_url)
        driver.get(f"{self.config['app_url']}/admin/topology/topology/")
