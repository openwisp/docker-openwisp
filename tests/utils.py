import unittest
from selenium.common.exceptions import NoSuchElementException


class TestUtilities(unittest.TestCase):
    def log_in(self, driver, app_url, username, password):
        """
        Log in to the admin dashboard
        Argument:
            driver: selenium driver
            app_url: domain to reach admin dashboard
                        example: http://dashboard.openwisp.org
            username: username to be used for login
            password: password to be used for login
        """
        driver.get(app_url + '/admin/login/')
        if 'admin/login' not in driver.current_url:
            return
        username_input = driver.find_element_by_name('username')
        password_input = driver.find_element_by_name('password')
        username_input.send_keys(username)
        password_input.send_keys(password)
        log_in_button = \
            (driver.find_element_by_class_name('submit-row')
                   .find_element_by_xpath('//input[@type="submit"]'))
        log_in_button.click()
        try:
            driver.find_element_by_class_name('logout')
        except NoSuchElementException:
            message = 'Login failed. Credentials used were username:' \
                      '{} & Password: {}'.format(username, password)

            self.fail(message)

    def get_error_js_logs(self, driver):
        """
        Return all js errors that occured
        Argument:
            driver: selenium driver
        """
        logs = driver.get_log('browser')
        js_errors = [logentry['message']
                     for logentry in logs if logentry['level'] == 'SEVERE']
        if js_errors:
            return js_errors
        else:
            return []

    def create_mobile_location(self, driver, app_url, location_name):
        """
        Create a new location with `location_name`
        Argument:
            driver: selenium driver
            app_url: domain to reach admin dashboard
                        example: http://dashboard.openwisp.org
            location_name: location to use for operation
        """
        driver.get(app_url + '/admin/geo/location/add/')
        organization_default = \
            (driver.find_element_by_name('organization')
                   .find_element_by_xpath('//option[text()="default"]'))
        organization_default.click()
        name = driver.find_element_by_name('name')
        name.send_keys(location_name)
        type_outdoor = \
            (driver.find_element_by_name('type')
                   .find_element_by_xpath('//option[@value="outdoor"]'))
        type_outdoor.click()
        is_mobile = driver.find_element_by_name('is_mobile')
        is_mobile.click()
        save_button = driver.find_element_by_name('_save')
        save_button.click()

    def get_location(self, driver, app_url, location_name):
        """
        Redirect to `location_name` form page
        Argument:
            driver: selenium driver
            app_url: domain to reach admin dashboard
                        example: http://dashboard.openwisp.org
            location_name: location to use for operation
        """
        driver.get(app_url + '/admin/geo/location/')
        location = driver.find_element_by_class_name('field-name')
        try:
            location.find_element_by_link_text(location_name).click()
        except NoSuchElementException:
            message = 'There is no location with {} name'.format(location_name)
            self.fail(message)

    def set_location_marker(self, driver, location_name):
        """
        Set marker on map on location object with location_name
        Argument:
            driver: selenium driver
            location_name: location to use for operation
        """
        marker_button = \
            driver.find_element_by_class_name('leaflet-draw-draw-marker')
        marker_button.click()
        geo_map = driver.find_element_by_id('id_geometry-map')
        geo_map.click()
        save_button = driver.find_element_by_name('_save')
        save_button.click()

    def delete_location(self, driver, app_url, location_name):
        """
        Delete the location element with location_name
        Argument:
            driver: selenium driver
            location_name: location to use for operation
        """
        self.get_location(driver, app_url, location_name)
        delete_button = \
            (driver.find_element_by_class_name('submit-row')
                   .find_element_by_class_name('deletelink-box'))
        delete_button.click()
        confirm_delete_button = \
            driver.find_element_by_xpath('//input[@type="submit"]')
        confirm_delete_button.click()
