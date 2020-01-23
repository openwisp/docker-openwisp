import time
import unittest
from urllib import request
from selenium import webdriver
from utils import TestUtilities


class Pretest(TestUtilities):

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
        for i in range(1, max_retries):
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
            self.fail("ERROR: openwisp-dashboard login page not reachable!")
        self.cleanUp()


class TestServices(TestUtilities):

    def test_websocket(self):
        """
        This test ensures that websocket service is running correctly
        using selenium by creating a new location, setting a map marker
        and checking if the location changed on a second window.
        It also checks for JavaScript errors on window console.
        """
        self.change_location_driver = webdriver.Chrome(
            options=self.chrome_options)
        self.location_name = 'automated-websocket-selenium-loc01'
        self.log_in(self.base_driver, self.config['app_url'],
                    self.config['username'], self.config['password'])
        self.create_mobile_location(self.base_driver,
                                    self.config['app_url'], self.location_name)
        self.get_location(self.base_driver,
                          self.config['app_url'], self.location_name)
        js_websocket_errors = []
        for error in self.get_error_js_logs(self.base_driver):
            if 'websocket' or 'ws' in error.lower():
                js_websocket_errors.append(error)
        if js_websocket_errors:
            self.fail('Following WebSocket related js errors occurred: ' +
                      ', '.join(js_websocket_errors))
        # assert that there is no markers on map
        self.assertEqual(len(self.base_driver
                                 .find_elements_by_class_name('leaflet-marker-icon')), 0)
        # create marker on another window
        self.log_in(self.change_location_driver, self.config['app_url'],
                    self.config['username'], self.config['password'])
        self.get_location(self.change_location_driver,
                          self.config['app_url'], self.location_name)
        self.set_location_marker(self.change_location_driver,
                                 self.location_name)
        # assert that marker popped up on map
        self.assertEqual(len(self.base_driver
                                 .find_elements_by_class_name('leaflet-marker-icon')), 1)
        self.delete_location(self.base_driver,
                             self.config['app_url'], self.location_name)
        self.change_location_driver.close()
        self.cleanUp()

    def test_admin_login(self):
        """
        This test is used to login into django-admin
        It will try to login to the admin dashboard using selenium
        """
        self.log_in(self.base_driver, self.config['app_url'],
                    self.config['username'], self.config['password'])
        self.cleanUp()


if __name__ == "__main__":
    unittest.main()
