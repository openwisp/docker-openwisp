import os
import subprocess
import time
import unittest
from urllib import request

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options as ChromiumOptions
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from utils import TestConfig, TestUtilities


class Pretest(TestConfig, unittest.TestCase):
    """
    Checks to perform before tests
    """

    def test_wait_for_services(self):
        """
        This test wait for services to be started up and check
        if the openwisp-dashboard login page is reachable.
        Should be called first before calling another test.
        """
        isServiceReachable = False
        max_retries = self.config['services_max_retries']
        delay_retries = self.config['services_delay_retries']
        admin_login_page = self.config['app_url'] + '/admin/login/'
        for _ in range(1, max_retries):
            try:
                # check if we can reach to admin login page
                # and the page return 200 OK status code
                if request.urlopen(admin_login_page).getcode() == 200:
                    isServiceReachable = True
                    break
            except Exception:
                # if error occured, retry to reach the admin
                # login page after delay_retries second(s)
                time.sleep(delay_retries)
        if not isServiceReachable:
            self.fail('ERROR: openwisp-dashboard login page not reachable!')


class TestServices(TestUtilities, unittest.TestCase):
    @property
    def failureException(self):
        TestServices.failed_test = True
        return super().failureException

    @classmethod
    def setUpClass(cls):
        cls.failed_test = False
        # Django Test Setup
        if cls.config['load_init_data']:
            test_data_file = os.path.join(
                os.path.dirname(os.path.realpath(__file__)), 'data.py'
            )
            entrypoint = "python manage.py shell --command='import data; data.setup()'"
            cmd = subprocess.Popen(
                [
                    'docker-compose',
                    'run',
                    '--rm',
                    '--entrypoint',
                    entrypoint,
                    '--volume',
                    test_data_file + ':/opt/openwisp/data.py',
                    'dashboard',
                ],
                universal_newlines=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=cls.root_location,
            )
            output, error = map(str, cmd.communicate())
            with open(cls.config['logs_file'], 'w') as logs_file:
                logs_file.write(output)
                logs_file.write(error)
            subprocess.run(
                ['docker-compose', 'up', '--detach'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=cls.root_location,
            )
        # Create base drivers (Firefox)
        if cls.config['driver'] == 'firefox':
            profile = webdriver.FirefoxProfile()
            profile.accept_untrusted_certs = True
            options = webdriver.FirefoxOptions()
            capabilities = DesiredCapabilities.FIREFOX
            capabilities['loggingPrefs'] = {'browser': 'ALL'}
            if cls.config['headless']:
                options.add_argument('-headless')
            cls.base_driver = webdriver.Firefox(
                options=options,
                capabilities=capabilities,
                service_log_path='/tmp/geckodriver.log',
                firefox_profile=profile,
            )
            cls.second_driver = webdriver.Firefox(
                options=options,
                capabilities=capabilities,
                service_log_path='/tmp/geckodriver.log',
                firefox_profile=profile,
            )
        # Create base drivers (Chromium)
        if cls.config['driver'] == 'chromium':
            chrome_options = ChromiumOptions()
            chrome_options.add_argument('--ignore-certificate-errors')
            capabilities = DesiredCapabilities.CHROME
            capabilities['goog:loggingPrefs'] = {'browser': 'ALL'}
            if cls.config['headless']:
                chrome_options.add_argument('--headless')
            cls.base_driver = webdriver.Chrome(
                options=chrome_options, desired_capabilities=capabilities
            )
            cls.second_driver = webdriver.Chrome(
                options=chrome_options, desired_capabilities=capabilities
            )
        cls.base_driver.set_window_size(1366, 768)
        cls.second_driver.set_window_size(1366, 768)

    @classmethod
    def tearDownClass(cls):
        for resource_link in cls.objects_to_delete:
            try:
                cls._delete_object(resource_link)
            except NoSuchElementException:
                print('Unable to delete resource at: ' + resource_link)
        cls.second_driver.close()
        cls.base_driver.close()
        if cls.failed_test and cls.config['logs']:
            cmd = subprocess.Popen(
                ['docker-compose', 'logs'],
                universal_newlines=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=cls.root_location,
            )
            output, _ = map(str, cmd.communicate())
            print('One of the containers are down!\nOutput:\n' + output)

    @classmethod
    def _delete_object(cls, resource_link):
        """
        Takes URL for location to delete.
        """
        cls.base_driver.get(resource_link)
        cls.base_driver.find_element_by_class_name(
            'submit-row'
        ).find_element_by_class_name('deletelink-box').click()
        cls.base_driver.find_element_by_xpath('//input[@type="submit"]').click()

    def test_topology_graph(self):
        path = '/admin/topology/topology'
        label = 'automated-selenium-test-02'
        self.login()
        self.create_network_topology(label)
        self.action_on_resource(label, path, 'delete_selected')
        self.assertNotIn('Nodes', self.base_driver.page_source)
        self.action_on_resource(label, path, 'update_selected')
        self.action_on_resource(label, path, 'delete_selected')
        self.assertIn('Nodes', self.base_driver.page_source)

    def test_admin_login(self):
        self.login()
        self.login(driver=self.second_driver)
        try:
            self.base_driver.find_element_by_class_name('logout')
            self.second_driver.find_element_by_class_name('logout')
        except NoSuchElementException:
            message = (
                'Login failed. Credentials used were username: '
                '{} & Password: {}'.format(
                    self.config['username'], self.config['password']
                )
            )
            self.fail(message)

    def test_console_errors(self):
        url_list = [
            '/admin/',
            '/admin/geo/location/add/',
            '/accounts/password/reset/',
            '/admin/config/device/add/',
            '/admin/config/template/add/',
            '/admin/openwisp_radius/radiuscheck/add/',
            '/admin/openwisp_radius/radiusgroup/add/',
            '/admin/openwisp_radius/radiusbatch/add/',
            '/admin/openwisp_radius/nas/add/',
            '/admin/openwisp_radius/radiusreply/',
            '/admin/geo/floorplan/add/',
            '/admin/topology/link/add/',
            '/admin/topology/node/add/',
            '/admin/topology/topology/add/',
            '/admin/pki/ca/add/',
            '/admin/pki/cert/add/',
            '/admin/openwisp_users/user/add/',
        ]
        change_form_list = [
            ['automated-selenium-location01', '/admin/geo/location/'],
            ['users', '/admin/openwisp_radius/radiusgroup/'],
            ['default-management-vpn', '/admin/config/template/'],
            ['default', '/admin/config/vpn/'],
            ['default', '/admin/pki/ca/'],
            ['default', '/admin/pki/cert/'],
            ['default', '/admin/openwisp_users/organization/'],
            ['test_superuser2', '/admin/openwisp_users/user/'],
        ]
        self.login()
        self.create_mobile_location('automated-selenium-location01')
        self.create_superuser('sample@email.com', 'test_superuser2')
        # url_list tests
        for url in url_list:
            self.base_driver.get(self.config['app_url'] + url)
            self.assertEqual([], self.console_error_check())
            self.assertIn('OpenWISP', self.base_driver.title)
        # change_form_list tests
        for change_form in change_form_list:
            self.get_resource(change_form[0], change_form[1])
            self.assertEqual([], self.console_error_check())
            self.assertIn('OpenWISP', self.base_driver.title)

    def test_websocket_marker(self):
        """
        This test ensures that websocket service is running correctly
        using selenium by creating a new location, setting a map marker
        and checking if the location changed on a second window.
        """
        location_name = 'automated-websocket-selenium-loc01'
        self.login()
        self.login(driver=self.second_driver)
        self.create_mobile_location(location_name)
        self.get_resource(location_name, '/admin/geo/location/')
        self.get_resource(
            location_name, '/admin/geo/location/', driver=self.second_driver
        )
        self.base_driver.find_element_by_name('is_mobile').click()
        mark = len(self.base_driver.find_elements_by_class_name('leaflet-marker-icon'))
        self.assertEqual(mark, 0)
        self.add_mobile_location_point(location_name, driver=self.second_driver)
        mark = len(self.base_driver.find_elements_by_class_name('leaflet-marker-icon'))
        self.assertEqual(mark, 1)

    def test_add_superuser(self):
        """
        Create new user to ensure a new user
        can be added.
        """
        self.login()
        self.create_superuser()
        self.assertEqual(
            'The user "test_superuser" was changed successfully.',
            self.base_driver.find_elements_by_class_name('success')[0].text,
        )

    def test_forgot_password(self):
        """
        Test forgot password to ensure that
        postfix is working properly.
        """
        self.base_driver.get(self.config['app_url'] + '/accounts/password/reset/')
        self.base_driver.find_element_by_name('email').send_keys('admin@example.com')
        self.base_driver.find_element_by_xpath('//input[@type="submit"]').click()
        self.assertIn(
            'We have sent you an e-mail. Please contact us if you '
            'do not receive it within a few minutes.',
            self.base_driver.page_source,
        )

    def test_celery(self):
        """
        Ensure celery and celery-beat tasks are registered.
        """
        cmd = subprocess.Popen(
            [
                'docker-compose',
                'run',
                '--rm',
                'celery',
                'celery',
                '-A',
                'openwisp',
                'inspect',
                'registered',
            ],
            universal_newlines=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.root_location,
        )
        output, error = map(str, cmd.communicate())
        if (
            ('openwisp.tasks.radius_tasks' not in output)
            or ('openwisp.tasks.save_snapshot' not in output)
            or ('openwisp.tasks.update_topology' not in output)
            or ('openwisp_controller.connection.tasks.update_config' not in output)
        ):
            self.fail(
                'Not all celery / celery-beat tasks are registered\nOutput:\n'
                + output
                + '\nError:\n'
                + error
            )

    def test_freeradius(self):
        """
        Ensure freeradius service is working correctly.
        """
        cmd = subprocess.Popen(
            [
                'docker',
                'run',
                '-it',
                '--rm',
                '--network',
                'docker-openwisp_default',
                '2stacks/radtest',
                'radtest',
                'admin',
                'admin',
                'freeradius',
                '0',
                'testing123',
            ],
            universal_newlines=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.root_location,
        )
        output, error = map(str, cmd.communicate())
        if 'Received Access-Accept' not in output:
            self.fail(
                'Request not Accepted!\nOutput:\n' + output + '\nError:\n' + error
            )

    def test_containers_down(self):
        """
        Ensure freeradius service is working correctly.
        """
        cmd = subprocess.Popen(
            ['docker-compose', 'ps'],
            universal_newlines=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.root_location,
        )
        output, error = map(str, cmd.communicate())
        if 'Exit' in output:
            self.fail(
                'One of the containers are down!\nOutput:\n'
                + output
                + '\nError:\n'
                + error
            )


if __name__ == '__main__':
    unittest.main(verbosity=3)
