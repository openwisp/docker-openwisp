import sys
import unittest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException


class TestUtilities:
    def log_in(self, driver):
        driver.get('http://dashboard.openwisp.org/admin/login/')
        if 'admin/login' not in driver.current_url:
            return
        username_input = driver.find_element_by_name('username')
        password_input = driver.find_element_by_name('password')
        username_input.send_keys('admin')
        password_input.send_keys('admin')
        log_in_button = (
            driver.find_element_by_class_name('submit-row').
            find_element_by_xpath('//input[@type="submit"]')
        )
        log_in_button.click()

    def get_error_js_logs(self, driver):
        # return all js errors that occured
        logs = driver.get_log('browser')
        js_errors = [logentry['message'] for logentry in logs if logentry['level'] == 'SEVERE']
        if js_errors:
            return js_errors
        else:
            return []

    def create_mobile_location(self, driver, location_name):
        driver.get('http://dashboard.openwisp.org/admin/geo/location/add/')
        organization_default = (
            driver.find_element_by_name('organization').
            find_element_by_xpath('//option[text()="default"]')
        )
        organization_default.click()
        name = driver.find_element_by_name('name')
        name.send_keys(location_name)
        type_outdoor = driver.find_element_by_name('type').find_element_by_xpath('//option[@value="outdoor"]')
        type_outdoor.click()
        is_mobile = driver.find_element_by_name('is_mobile')
        is_mobile.click()
        save_button = driver.find_element_by_name('_save')
        save_button.click()

    def get_location(self, driver, location_name):
        # redirects to location with given name
        driver.get('http://dashboard.openwisp.org/admin/geo/location/')
        location = driver.find_element_by_class_name('field-name')
        try:
            if location.find_element_by_link_text(location_name):
                return location.find_element_by_link_text(location_name).click()
        except NoSuchElementException:
            message = 'There is no location with {} name'.format(location_name)
            self.fail(message)

    def set_location_marker(self, driver, location_name):
        # set marker on map on location object
        self.get_location(driver, location_name)
        marker_button = driver.find_element_by_class_name('leaflet-draw-draw-marker')
        marker_button.click()
        geo_map = driver.find_element_by_id('id_geometry-map')
        geo_map.click()
        save_button = driver.find_element_by_name('_save')
        save_button.click()

    def delete_location(self, driver, location_name):
        self.get_location(driver, location_name)
        delete_button = (
            driver.find_element_by_class_name('submit-row').
            find_element_by_class_name('deletelink-box')
        )
        delete_button.click()
        confirm_delete_button = (
            driver.
            find_element_by_xpath('//div/div[@id="content"]/form/div/input[@type="submit"]')
        )
        confirm_delete_button.click()


class TestWebSocket(TestUtilities, unittest.TestCase):
    is_headless = False

    def setUp(self):
        self.chrome_options = Options()
        if self.is_headless:
            self.chrome_options.add_argument("--headless")
        self.base_driver = webdriver.Chrome(options=self.chrome_options)
        self.location_name = 'automated-websocket-selenium-loc01'

    def tearDown(self):
        self.delete_location(self.base_driver, self.location_name)
        self.base_driver.close()

    def test_websocket(self):
        self.log_in(self.base_driver)
        self.create_mobile_location(self.base_driver, self.location_name)
        self.get_location(self.base_driver, self.location_name)
        js_websocket_errors = []
        for error in self.get_error_js_logs(self.base_driver):
            if 'websocket' or 'ws' in error.lower():
                js_websocket_errors.append(error)
        if js_websocket_errors:
            self.fail('Following WebSocket related js errors occurred: ' + ', '.join(js_websocket_errors))
        # assert that there is no markers on map
        self.assertEqual(len(self.base_driver.find_elements_by_class_name('leaflet-marker-icon')), 0)
        change_location_driver = webdriver.Chrome(options=self.chrome_options)
        self.log_in(change_location_driver)
        self.set_location_marker(change_location_driver, self.location_name)
        change_location_driver.close()
        # assert that marker popped up on map
        self.assertEqual(len(self.base_driver.find_elements_by_class_name('leaflet-marker-icon')), 1)


if __name__ == '__main__':
    # To run tests in chrome headless mode pass --headless command line argument
    if '--headless' in sys.argv:
        sys.argv.remove('--headless')
        TestWebSocket.is_headless = True
    unittest.main()
