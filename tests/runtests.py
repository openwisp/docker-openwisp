import os
import subprocess
import time
import unittest
from urllib import error as urlerror
from urllib import request

import requests
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from utils import TestUtilities


class Pretest(TestUtilities, unittest.TestCase):
    """Checks to perform before tests"""

    def test_wait_for_services(self):
        """This test wait for services to be started up.

        Then checks if the openwisp-dashboard login page is reachable.
        Should be called first before calling another test.
        """

        isServiceReachable = False
        max_retries = self.config['services_max_retries']
        delay_retries = self.config['services_delay_retries']
        admin_login_page = f"{self.config['app_url']}/admin/login/"
        for _ in range(1, max_retries):
            try:
                # check if we can reach to admin login page
                # and the page return 200 OK status code
                if request.urlopen(admin_login_page, context=self.ctx).getcode() == 200:
                    isServiceReachable = True
                    break
            except (urlerror.HTTPError, OSError, ConnectionResetError):
                # if error occurred, retry to reach the admin
                # login page after delay_retries second(s)
                time.sleep(delay_retries)
        if not isServiceReachable:
            self.fail('ERROR: openwisp-dashboard login page not reachable!')

        # Ensure all celery workers are online
        container_id = self.docker_compose_get_container_id('celery')
        celery_container = self.docker_client.containers.get(container_id)
        for _ in range(0, max_retries):
            result = celery_container.exec_run('celery -A openwisp status')
            online_workers = result.output.decode('utf-8').split('\n')[-2]
            try:
                assert online_workers == '5 nodes online.'
                break
            except AssertionError:
                # if error occurred, retry to reach the celery workers
                # after delay_retries second(s)
                time.sleep(delay_retries)
        else:
            self.fail(f'All celery workers are not online: {online_workers}')


class TestServices(TestUtilities, unittest.TestCase):
    @property
    def failureException(self):
        TestServices.failed_test = True
        return super().failureException

    @classmethod
    def setUpClass(cls):
        cls.failed_test = False
        cls.live_server_url = cls.config['app_url']
        cls.admin_username = cls.config['username']
        cls.admin_password = cls.config['password']
        # Django Test Setup
        if cls.config['load_init_data']:
            test_data_file = os.path.join(
                os.path.dirname(os.path.realpath(__file__)), 'data.py'
            )
            entrypoint = "python manage.py shell --command='import data; data.setup()'"
            cmd = subprocess.Popen(
                [
                    'docker',
                    'compose',
                    'run',
                    '--rm',
                    '--entrypoint',
                    entrypoint,
                    '--volume',
                    f'{test_data_file}:/opt/openwisp/data.py',
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
                ['docker', 'compose', 'up', '--detach'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=cls.root_location,
            )
        # Create base drivers (Firefox)
        if cls.config['driver'] == 'firefox':
            cls.base_driver = cls.get_firefox_webdriver()
            cls.second_driver = cls.get_firefox_webdriver()
        # Create base drivers (Chromium)
        if cls.config['driver'] == 'chromium':
            cls.base_driver = cls.get_chrome_webdriver()
            cls.second_driver = cls.get_chrome_webdriver()
        cls.web_driver = cls.base_driver

    @classmethod
    def tearDownClass(cls):
        for resource_link in cls.objects_to_delete:
            try:
                cls._delete_object(resource_link)
            except NoSuchElementException:
                print(f'Unable to delete resource at: {resource_link}')
        cls.second_driver.quit()
        cls.base_driver.quit()
        if cls.failed_test and cls.config['logs']:
            cmd = subprocess.Popen(
                ['docker', 'compose', 'logs'],
                universal_newlines=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=cls.root_location,
            )
            output, _ = map(str, cmd.communicate())
            print(f'One of the containers are down!\nOutput:\n{output}')

    @classmethod
    def _delete_object(cls, resource_link):
        """Takes URL for location to delete."""
        cls.base_driver.get(resource_link)
        element = cls.base_driver.find_element(By.CLASS_NAME, 'deletelink-box')
        js = "arguments[0].setAttribute('style', 'display:block')"
        cls.base_driver.execute_script(js, element)
        element.find_element(By.CLASS_NAME, 'deletelink').click()
        cls.base_driver.find_element(By.XPATH, '//input[@type="submit"]').click()

    def test_topology_graph(self):
        path = '/admin/topology/topology'
        label = 'automated-selenium-test-02'
        self.login()
        self.create_network_topology(label)
        self.get_resource(label, path, select_field='field-label')
        # Click on "Visualize topology graph" button
        self.find_element(By.CSS_SELECTOR, 'input.visualizelink').click()
        # Click on sidebar handle
        self.find_element(By.CSS_SELECTOR, 'button.sideBarHandle').click()
        # Verify topology label
        self.assertEqual(
            self.find_element(By.CSS_SELECTOR, '.njg-valueLabel').text.lower(),
            label,
        )
        try:
            console_logs = self.console_error_check()
            self.assertEqual(len(console_logs), 0)
        except AssertionError:
            print('Browser console logs', console_logs)
            self.fail()
        self.action_on_resource(label, path, 'delete_selected')
        self.assertNotIn('<li>Nodes: ', self.web_driver.page_source)
        self.action_on_resource(label, path, 'update_selected')

        self.action_on_resource(label, path, 'delete_selected')
        self._wait_until_page_ready()
        self.assertIn('<li>Nodes: ', self.web_driver.page_source)

    def test_admin_login(self):
        self.login()
        self.login(driver=self.second_driver)
        try:
            self.wait_for_presence(By.CLASS_NAME, 'logout')
            self.wait_for_presence(By.CLASS_NAME, 'logout', driver=self.second_driver)
        except TimeoutError:
            message = (
                'Login failed. Credentials used were username: '
                f"{self.config['username']} & Password: {self.config['password']}"
            )
            self.fail(message)

    def test_device_monitoring_charts(self):
        self.login()
        self.get_resource('test-device', '/admin/config/device/')
        self.find_element(By.CSS_SELECTOR, 'ul.tabs li.charts').click()
        try:
            WebDriverWait(self.base_driver, 3).until(EC.alert_is_present())
        except TimeoutException:
            # No alert means that the request to fetch
            # monitoring charts was successful.
            pass
        else:
            # When the request to fetch monitoring charts fails,
            # an error is shown.
            self.fail('An alert was found on the device chart page.')

    def test_default_topology(self):
        self.login()
        self.get_resource(
            'test-device', '/admin/topology/topology/', select_field='field-label'
        )

    def test_create_prefix_users(self):
        self.login()
        prefix_objname = 'automated-prefix-test-01'
        # Create prefix users
        self.open('/admin/openwisp_radius/radiusbatch/add/')
        self.find_element(By.NAME, 'strategy').find_element(
            By.XPATH, '//option[@value="prefix"]'
        ).click()
        self.find_element(By.NAME, 'organization').find_element(
            By.XPATH, '//option[text()="default"]'
        ).click()
        self.find_element(By.NAME, 'name').send_keys(prefix_objname)
        self.find_element(By.NAME, 'prefix').send_keys('automated-prefix')
        self.find_element(By.NAME, 'number_of_users').send_keys('1')
        self.find_element(By.NAME, '_save').click()
        # Check PDF available
        self.get_resource(prefix_objname, '/admin/openwisp_radius/radiusbatch/')
        self.objects_to_delete.append(self.base_driver.current_url)
        prefix_pdf_file_path = self.base_driver.find_element(
            By.XPATH, '//a[text()="Download User Credentials"]'
        ).get_property('href')
        reqHeader = {
            'Cookie': f"sessionid={self.base_driver.get_cookies()[0]['value']}"
        }
        curlRequest = request.Request(prefix_pdf_file_path, headers=reqHeader)
        try:
            if request.urlopen(curlRequest, context=self.ctx).getcode() != 200:
                raise ValueError
        except (urlerror.HTTPError, OSError, ConnectionResetError, ValueError) as error:
            self.fail(f'Cannot download PDF file: {error}')

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
            '/admin/firmware_upgrader/build/',
            '/admin/firmware_upgrader/build/add/',
            '/admin/firmware_upgrader/category/',
            '/admin/firmware_upgrader/category/add/',
        ]
        change_form_list = [
            ['automated-selenium-location01', '/admin/geo/location/'],
            ['users', '/admin/openwisp_radius/radiusgroup/'],
            ['default-management-vpn', '/admin/config/template/'],
            ['default', '/admin/config/vpn/'],
            ['default', '/admin/pki/ca/'],
            ['default', '/admin/pki/cert/'],
            ['default', '/admin/openwisp_users/organization/'],
            ['test_superuser2', '/admin/openwisp_users/user/', 'field-username'],
        ]
        self.login()
        self.create_mobile_location('automated-selenium-location01')
        self.create_superuser('sample@email.com', 'test_superuser2')
        # url_list tests
        for url in url_list:
            self.open(url)
            self.assertEqual([], self.console_error_check())
            self.assertIn('OpenWISP', self.base_driver.title)
        # change_form_list tests
        for change_form in change_form_list:
            self.get_resource(*change_form)
            self.assertEqual([], self.console_error_check())
            self.assertIn('OpenWISP', self.base_driver.title)

    def test_websocket_marker(self):
        """Ensures that the websocket service is running correctly.

        This test uses selenium, it creates a new location, sets a map
        marker and checks if the location changed int a second window.
        """
        location_name = 'automated-websocket-selenium-loc01'
        self.login()
        self.login(driver=self.second_driver)
        self.create_mobile_location(location_name)
        self.get_resource(location_name, '/admin/geo/location/')
        self.get_resource(
            location_name, '/admin/geo/location/', driver=self.second_driver
        )
        self.find_element(By.NAME, 'is_mobile', driver=self.base_driver).click()
        mark = len(
            self.find_elements(
                By.CLASS_NAME, 'leaflet-marker-icon', wait_for='invisibility'
            )
        )
        self.assertEqual(mark, 0)
        self.add_mobile_location_point(location_name, driver=self.second_driver)
        mark = len(
            self.find_elements(
                By.CLASS_NAME, 'leaflet-marker-icon', wait_for='presence'
            )
        )
        self.assertEqual(mark, 1)

    def test_add_superuser(self):
        """Create new user to ensure a new user can be added."""
        self.login()
        self.create_superuser()
        self.assertEqual(
            'The user “test_superuser” was changed successfully.',
            self.find_element(By.CLASS_NAME, 'success').text,
        )

    def test_forgot_password(self):
        """Test forgot password to ensure that postfix is working properly."""

        self.open('/accounts/password/reset/')
        self.find_element(By.NAME, 'email').send_keys('admin@example.com')
        self.find_element(By.XPATH, '//button[@type="submit"]').click()
        self._wait_until_page_ready()
        self.assertIn(
            'We have sent you an email. If you have not received '
            'it please check your spam folder. Otherwise contact us '
            'if you do not receive it in a few minutes.',
            self.base_driver.page_source,
        )

    def test_celery(self):
        """Ensure celery and celery-beat tasks are registered."""
        expected_output_list = [
            'djcelery_email_send_multiple',
            'openwisp.tasks.radius_tasks',
            'openwisp.tasks.save_snapshot',
            'openwisp.tasks.update_topology',
            'openwisp_controller.config.tasks.change_devices_templates',
            'openwisp_controller.config.tasks.create_vpn_dh',
            'openwisp_controller.config.tasks.invalidate_devicegroup_cache_change',
            'openwisp_controller.config.tasks.invalidate_devicegroup_cache_delete',
            'openwisp_controller.config.tasks.invalidate_vpn_server_devices_cache_change',  # noqa: E501
            'openwisp_controller.config.tasks.trigger_vpn_server_endpoint',
            'openwisp_controller.config.tasks.update_template_related_config_status',
            'openwisp_controller.connection.tasks.auto_add_credentials_to_devices',
            'openwisp_controller.connection.tasks.launch_command',
            'openwisp_controller.connection.tasks.update_config',
            'openwisp_controller.subnet_division.tasks.provision_extra_ips',
            'openwisp_controller.subnet_division.tasks.provision_subnet_ip_for_existing_devices',  # noqa: E501
            'openwisp_controller.subnet_division.tasks.update_subnet_division_index',
            'openwisp_controller.subnet_division.tasks.update_subnet_name_description',
            'openwisp_firmware_upgrader.tasks.batch_upgrade_operation',
            'openwisp_firmware_upgrader.tasks.create_all_device_firmwares',
            'openwisp_firmware_upgrader.tasks.create_device_firmware',
            'openwisp_firmware_upgrader.tasks.upgrade_firmware',
            'openwisp_monitoring.check.tasks.auto_create_config_check',
            'openwisp_monitoring.check.tasks.auto_create_iperf3_check',
            'openwisp_monitoring.check.tasks.auto_create_ping',
            'openwisp_monitoring.check.tasks.perform_check',
            'openwisp_monitoring.check.tasks.run_checks',
            'openwisp_monitoring.device.tasks.delete_wifi_clients_and_sessions',
            'openwisp_monitoring.device.tasks.offline_device_close_session',
            'openwisp_monitoring.device.tasks.trigger_device_checks',
            'openwisp_monitoring.device.tasks.write_device_metrics',
            'openwisp_monitoring.device.tasks.handle_disabled_organization',
            'openwisp_monitoring.monitoring.tasks.delete_timeseries',
            'openwisp_monitoring.monitoring.tasks.migrate_timeseries_database',
            'openwisp_monitoring.monitoring.tasks.timeseries_batch_write',
            'openwisp_monitoring.monitoring.tasks.timeseries_write',
            'openwisp_monitoring.monitoring.tasks.delete_timeseries',
            'openwisp_notifications.tasks.delete_ignore_object_notification',
            'openwisp_notifications.tasks.delete_notification',
            'openwisp_notifications.tasks.delete_obsolete_objects',
            'openwisp_notifications.tasks.delete_old_notifications',
            'openwisp_notifications.tasks.ns_organization_created',
            'openwisp_notifications.tasks.ns_organization_user_deleted',
            'openwisp_notifications.tasks.ns_register_unregister_notification_type',
            'openwisp_notifications.tasks.update_org_user_notificationsetting',
            'openwisp_notifications.tasks.update_superuser_notification_settings',
            'openwisp_radius.tasks.cleanup_stale_radacct',
            'openwisp_radius.tasks.convert_called_station_id',
            'openwisp_radius.tasks.deactivate_expired_users',
            'openwisp_radius.tasks.delete_old_postauth',
            'openwisp_radius.tasks.delete_old_radacct',
            'openwisp_radius.tasks.delete_old_radiusbatch_users',
            'openwisp_radius.tasks.delete_unverified_users',
            'openwisp_radius.tasks.perform_change_of_authorization',
            'openwisp_radius.tasks.send_login_email',
        ]

        def _test_celery_task_registered(container_name):
            container_id = self.docker_compose_get_container_id(container_name)
            celery_container = self.docker_client.containers.get(container_id)
            result = celery_container.exec_run('celery -A openwisp inspect registered')
            self.assertEqual(result.exit_code, 0)

            output = result.output.decode('utf-8')
            for expected_output in expected_output_list:
                if expected_output not in output:
                    self.fail(
                        'Not all celery / celery-beat tasks are registered.\n'
                        f'Expected celery task not found:\n{expected_output}'
                    )

        with self.subTest('Test celery container'):
            _test_celery_task_registered('celery')

        with self.subTest('Test celery_monitoring container'):
            _test_celery_task_registered('celery_monitoring')

    def test_radius_user_registration(self):
        """Ensure users can register using the RADIUS API."""
        url = f'{self.config["api_url"]}/api/v1/radius/organization/default/account/'
        response = requests.post(
            url,
            json={
                'username': 'signup-user',
                'email': 'user@signup.com',
                'password1': 'rLx6OH%[',
                'password2': 'rLx6OH%[',
            },
            verify=False,
        )
        self.assertEqual(response.status_code, 201)
        # Delete the created user
        self.login()
        self.get_resource(
            'signup-user', '/admin/openwisp_users/user/', 'field-username'
        )
        self.objects_to_delete.append(self.base_driver.current_url)

    def test_freeradius(self):
        """Ensure freeradius service is working correctly."""
        token_page = (
            f"{self.config['api_url']}/api/v1/radius/"
            'organization/default/account/token/'
        )
        request_body = 'username=admin&password=admin'.encode('utf-8')
        request_info = request.Request(token_page, data=request_body)
        try:
            response = request.urlopen(request_info, context=self.ctx)
        except (urlerror.HTTPError, OSError, ConnectionResetError):
            self.fail(f"Couldn't get radius-token, check {self.config['api_url']}")
        self.assertIn('"is_active":true', response.read().decode())

        container_id = self.docker_compose_get_container_id('freeradius')
        freeradius_container = self.docker_client.containers.get(container_id)
        freeradius_container.exec_run('apk add freeradius freeradius-radclient')
        result = freeradius_container.exec_run(
            'radtest admin admin localhost 0 testing123'
        )
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Received Access-Accept', result.output.decode('utf-8'))

        remove_tainted_container = [
            'docker compose rm -sf freeradius',
            'docker compose up -d freeradius',
        ]
        for command in remove_tainted_container:
            subprocess.Popen(
                command.split(),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=self.root_location,
            ).communicate()

    def test_containers_down(self):
        """Ensure freeradius service is working correctly."""
        cmd = subprocess.Popen(
            ['docker', 'compose', 'ps'],
            universal_newlines=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.root_location,
        )
        output, error = map(str, cmd.communicate())
        if 'Exit' in output:
            self.fail(
                f'One of the containers are down!\nOutput:\n{output}\nError:\n{error}'
            )


if __name__ == '__main__':
    suite = unittest.TestSuite()
    suite.addTest(TestServices('test_topology_graph'))
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
