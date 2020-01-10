import os
import json
import unittest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from utils import TestUtilities


class TestWebSocket(TestUtilities):

    def setUp(self):
        config_file = os.path.join(os.path.dirname(__file__), "config.json")
        with open(config_file) as json_file:
            self.config = json.load(json_file)
        self.chrome_options = Options()
        self.chrome_options.add_argument('--ignore-certificate-errors')
        if self.config['headless']:
            self.chrome_options.add_argument("--headless")
        self.base_driver = webdriver.Chrome(options=self.chrome_options)
        self.change_location_driver = webdriver.Chrome(
            options=self.chrome_options)
        self.location_name = 'automated-websocket-selenium-loc01'

    def cleanUp(self):
        self.delete_location(self.base_driver,
                             self.config['app_url'], self.location_name)
        self.base_driver.close()
        self.change_location_driver.close()

    def test_websocket(self):
        """
        This test ensures that websocket service is running correctly
        using selenium by creating a new location, setting a map marker
        and checking if the location changed on a second window.
        It also checks for JavaScript errors on window console.
        """
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
        self.log_in(self.change_location_driver,
                    self.config['app_url'], self.config['username'], self.config['password'])
        self.get_location(self.change_location_driver,
                          self.config['app_url'], self.location_name)
        self.set_location_marker(self.change_location_driver,
                                 self.location_name)
        # assert that marker popped up on map
        self.assertEqual(len(self.base_driver
                                 .find_elements_by_class_name('leaflet-marker-icon')), 1)
        self.cleanUp()


if __name__ == "__main__":
    unittest.main()
