import json
import os
import subprocess
import tempfile
import time
import unittest
from contextlib import contextmanager
from pathlib import Path
from urllib import error as urlerror
from urllib import request
from urllib.parse import urlsplit, urlunsplit

import requests
from scripts.precompress_static import ASSETS
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from utils import BaseTestUtils, FunctionalTestUtils

TEST_TOPOLOGY_ID = "00000000-0000-0000-0000-000000000000"


# 0 in the name is on purpose for alphabetical discovery
class Test0Preconditions(BaseTestUtils, unittest.TestCase):
    """Checks to perform before tests"""

    def test_wait_for_services(self):
        """This test wait for services to be started up.

        Then checks if the openwisp-dashboard login page is reachable.
        Should be called first before calling another test.
        """

        isServiceReachable = False
        max_retries = self.config["services_max_retries"]
        delay_retries = self.config["services_delay_retries"]
        for _ in range(1, max_retries):
            try:
                admin_login_page = (
                    f"{self.config['app_url']}{self.reverse_url('admin:login')}"
                )
                # check if we can reach to admin login page
                # and the page return 200 OK status code
                if request.urlopen(admin_login_page, context=self.ctx).getcode() == 200:
                    isServiceReachable = True
                    break
            except (RuntimeError, urlerror.HTTPError, OSError, ConnectionResetError):
                # if error occurred, retry to reach the admin
                # login page after delay_retries second(s)
                time.sleep(delay_retries)
        if not isServiceReachable:
            self.fail("ERROR: openwisp-dashboard login page not reachable!")

        # Ensure all celery workers are online
        container_id = self.docker_compose_get_container_id("celery")
        celery_container = self.docker_client.containers.get(container_id)
        for _ in range(0, max_retries):
            result = celery_container.exec_run("celery -A openwisp status")
            online_workers = result.output.decode("utf-8").split("\n")[-2]
            try:
                assert online_workers == "5 nodes online."
                break
            except AssertionError:
                # if error occurred, retry to reach the celery workers
                # after delay_retries second(s)
                time.sleep(delay_retries)
        else:
            self.fail(f"All celery workers are not online: {online_workers}")


class Test1Dashboard(BaseTestUtils, unittest.TestCase):
    def test_dashboard_uses_same_origin_api_urls(self):
        """Ensure dashboard browser requests use module default relative URLs."""
        output, _ = self._execute_django_shell_command(
            "from openwisp_controller.settings import OPENWISP_CONTROLLER_API_HOST; "
            "from openwisp_firmware_upgrader.settings import FIRMWARE_API_BASEURL; "
            "from openwisp_monitoring.settings import MONITORING_API_BASEURL; "
            "from openwisp_network_topology.settings import TOPOLOGY_API_BASEURL; "
            "from openwisp_notifications.settings import HOST; "
            "from openwisp_radius.settings import RADIUS_API_BASEURL; "
            "print(OPENWISP_CONTROLLER_API_HOST, FIRMWARE_API_BASEURL, "
            "MONITORING_API_BASEURL, TOPOLOGY_API_BASEURL, HOST, "
            "RADIUS_API_BASEURL)"
        )
        self.assertEqual(
            output.strip().splitlines()[-1],
            "None / None None None /",
            "Dashboard API URLs must use same-origin module defaults.",
        )

    def test_dashboard_resolves_topology_api_urls(self):
        topology_url = self.reverse_url(
            "network_graph", kwargs={"pk": TEST_TOPOLOGY_ID}
        )
        output, _ = self._execute_django_shell_command(
            "from django.urls import is_valid_path; "
            f"print(bool(is_valid_path({topology_url!r})))"
        )
        self.assertEqual(
            output.strip().splitlines()[-1],
            "True",
            "Dashboard must serve topology API URLs.",
        )

    def test_dashboard_excludes_disabled_topology_api_urls(self):
        topology_url = self.reverse_url(
            "network_graph", kwargs={"pk": TEST_TOPOLOGY_ID}
        )
        output, _ = self._execute_django_shell_command(
            "from django.urls import is_valid_path; "
            f"print(bool(is_valid_path({topology_url!r})))",
            environment={"USE_OPENWISP_TOPOLOGY": "False"},
        )
        self.assertEqual(
            output.strip().splitlines()[-1],
            "False",
            "Dashboard must not serve disabled topology API URLs.",
        )

    def test_dashboard_resolves_radius_api_urls(self):
        radius_url = self.reverse_url(
            "radius:rest_register", kwargs={"slug": "default"}
        )
        output, _ = self._execute_django_shell_command(
            "from django.urls import is_valid_path; "
            f"print(bool(is_valid_path({radius_url!r})))"
        )
        self.assertEqual(
            output.strip().splitlines()[-1],
            "True",
            "Dashboard must serve RADIUS API URLs.",
        )

    def test_dashboard_excludes_disabled_radius_api_urls(self):
        radius_url = self.reverse_url(
            "radius:rest_register", kwargs={"slug": "default"}
        )
        output, _ = self._execute_django_shell_command(
            "from django.urls import is_valid_path; "
            f"print(bool(is_valid_path({radius_url!r})))",
            environment={"USE_OPENWISP_RADIUS": "False"},
        )
        self.assertEqual(
            output.strip().splitlines()[-1],
            "False",
            "Dashboard must not serve disabled RADIUS API URLs.",
        )

    def test_dashboard_channels_redis_socket_timeout(self):
        channel_redis_url = "redis://redis:6379/1"
        output, _ = self._execute_django_shell_command(
            "from django.conf import settings; import json; print(json.dumps("
            "settings.CHANNEL_LAYERS['default']['CONFIG']['hosts'][0]))",
            environment={"CHANNEL_REDIS_URL": channel_redis_url},
        )
        self.assertEqual(
            json.loads(output.strip().splitlines()[-1]),
            {"address": channel_redis_url, "socket_timeout": None},
            "Channels Redis host must have an unlimited socket timeout.",
        )


class TestInitialData(BaseTestUtils, unittest.TestCase):
    """Tests for default data created before the dashboard starts."""

    def test_names_do_not_select_initial_data(self):
        script = Path(__file__).parent / "scripts" / "initial_data.py"
        output, _ = self._execute_docker_compose_command(
            [
                "docker",
                "compose",
                "run",
                "--rm",
                "--no-deps",
                "--volume",
                f"{script}:/test_initial_data.py:ro",
                "--entrypoint",
                "python",
                "dashboard",
                "manage.py",
                "shell",
                "-c",
                "exec(open('/test_initial_data.py').read())",
            ],
            use_text_mode=True,
        )
        self.assertEqual(
            output.strip().splitlines()[-1], "initial data selectors passed"
        )


class TestServices(FunctionalTestUtils, unittest.TestCase):
    custom_static_token = None
    custom_settings_path = (
        Path(BaseTestUtils.root_location)
        / "customization"
        / "configuration"
        / "django"
        / "custom_django_settings.py"
    )

    @property
    def failureException(self):
        TestServices.failed_test = True
        return super().failureException

    @classmethod
    def _setup_admin_theme_links(cls):
        """Configure custom assets before creating Selenium sessions."""
        cls.custom_settings_existed = cls.custom_settings_path.exists()
        if cls.custom_settings_existed:
            cls.custom_settings = cls.custom_settings_path.read_text()
        cls.addClassCleanup(cls._cleanup_admin_theme_links)
        cls.custom_static_token = str(time.time_ns())
        cls.custom_css_path = (
            Path(cls.root_location)
            / "customization"
            / "theme"
            / "custom"
            / cls.config["custom_css_filename"]
        )
        cls.custom_css_directory_existed = cls.custom_css_path.parent.exists()
        cls.custom_css_path.parent.mkdir(parents=True, exist_ok=True)
        cls.custom_css_path.write_text(
            f"body{{--openwisp-test: {cls.custom_static_token};}}"
        )
        theme_links = [
            {
                "type": "text/css",
                "href": "/static/admin/css/openwisp.css",
                "rel": "stylesheet",
                "media": "all",
            },
            {
                "type": "text/css",
                "href": f"/static/custom/{cls.config['custom_css_filename']}",
                "rel": "stylesheet",
                "media": "all",
            },
            {
                "type": "image/svg+xml",
                "href": "/static/ui/openwisp/images/favicon.svg",
                "rel": "icon",
            },
        ]
        with cls.custom_settings_path.open("a") as custom_settings:
            custom_settings.write(f"\nOPENWISP_ADMIN_THEME_LINKS = {theme_links!r}\n")
        cls._execute_docker_compose_command(
            ["docker", "compose", "up", "--detach", "--force-recreate", "dashboard"]
        )
        for _ in range(cls.config["services_max_retries"]):
            try:
                admin_login_page = (
                    f"{cls.config['app_url']}{cls.reverse_url('admin:login')}"
                )
                if request.urlopen(admin_login_page, context=cls.ctx, timeout=10):
                    return
            except (RuntimeError, urlerror.HTTPError, OSError, ConnectionResetError):
                time.sleep(cls.config["services_delay_retries"])
        raise RuntimeError(
            "Dashboard did not start after applying test theme settings."
        )

    @classmethod
    def _cleanup_admin_theme_links(cls):
        if cls.custom_settings_existed:
            cls.custom_settings_path.write_text(cls.custom_settings)
        else:
            cls.custom_settings_path.unlink(missing_ok=True)
        cls.custom_css_path.unlink(missing_ok=True)
        if not cls.custom_css_directory_existed:
            cls.custom_css_path.parent.rmdir()
        cls._execute_docker_compose_command(
            ["docker", "compose", "up", "--detach", "--force-recreate", "dashboard"]
        )

    @classmethod
    def _cleanup_stale_test_data(cls):
        """Delete test-created users that may remain from a previous failed run.

        Runs before tests start so each CI attempt begins with a clean
        slate. Uses the Django ORM directly (via docker compose exec) to
        avoid any Selenium dependency during setup.
        """
        try:
            cls.delete_test_users("signup-user", "test_superuser", "test_superuser2")
        except Exception as e:
            exc_type = type(e).__name__
            print(
                f"Warning: stale test data cleanup failed ({exc_type}: {e}). "
                "Individual tests may fail if stale data is present."
            )

    @classmethod
    def setUpClass(cls):
        cls.failed_test = False
        cls.live_server_url = cls.config["app_url"]
        cls.admin_username = cls.config["username"]
        cls.admin_password = cls.config["password"]
        # Django Test Setup
        if cls.config["load_init_data"]:
            test_data_file = os.path.join(
                os.path.dirname(os.path.realpath(__file__)), "data.py"
            )
            entrypoint = "python manage.py shell --command='import data; data.setup()'"
            cls._execute_docker_compose_command(
                [
                    "docker",
                    "compose",
                    "run",
                    "--rm",
                    "--entrypoint",
                    entrypoint,
                    "--volume",
                    f"{test_data_file}:/opt/openwisp/data.py",
                    "dashboard",
                ]
            )
            cls._execute_docker_compose_command(
                ["docker", "compose", "up", "--detach"],
            )
        cls._setup_admin_theme_links()
        cls._cleanup_stale_test_data()
        # Create base drivers (Firefox)
        if cls.config["driver"] == "firefox":
            cls.base_driver = cls.get_firefox_webdriver()
            cls.second_driver = cls.get_firefox_webdriver()
        # Create base drivers (Chromium)
        if cls.config["driver"] == "chromium":
            cls.base_driver = cls.get_chrome_webdriver()
            cls.second_driver = cls.get_chrome_webdriver()
        cls.web_driver = cls.base_driver

    @classmethod
    def tearDownClass(cls):
        try:
            cls.delete_test_users(*cls.test_usernames_to_delete)
            cls.test_usernames_to_delete.clear()
        except Exception as e:
            exc_type = type(e).__name__
            print(f"Unable to delete test users: {exc_type}: {e}")
        cls.second_driver.quit()
        cls.base_driver.quit()
        if cls.failed_test and cls.config["logs"]:
            cmd = subprocess.Popen(
                ["docker", "compose", "logs"],
                universal_newlines=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=cls.root_location,
            )
            output, _ = map(str, cmd.communicate())
            print(f"One of the containers are down!\nOutput:\n{output}")

    def test_admin_login(self):
        self.login()
        self.login(driver=self.second_driver)
        try:
            self.wait_for_presence(By.CLASS_NAME, "logout")
            self.wait_for_presence(By.CLASS_NAME, "logout", driver=self.second_driver)
        except TimeoutError:
            message = (
                "Login failed. Credentials used were username: "
                f"{self.config['username']} & Password: {self.config['password']}"
            )
            self.fail(message)

    def test_dev_mode_admin_access(self):
        """Ensure the development profile permits browser access to the admin."""
        app_url = urlsplit(self.config["app_url"])
        login_url = self.reverse_url("admin:login")
        http_url = urlunsplit(("http", app_url.netloc, login_url, "", ""))
        https_url = urlunsplit(("https", app_url.netloc, login_url, "", ""))
        http_response = requests.get(http_url, allow_redirects=False, timeout=10)
        https_response = request.urlopen(https_url, context=self.ctx, timeout=10)
        self.assertEqual(
            http_response.status_code,
            200,
            "DEV_MODE must serve the admin login page over HTTP without a redirect.",
        )
        self.assertEqual(
            https_response.headers.get("Strict-Transport-Security"),
            "max-age=0",
            "DEV_MODE must clear previously cached HSTS policies.",
        )
        output, _ = self._execute_django_shell_command(
            "from django.conf import settings; "
            "print(*settings.CORS_ALLOWED_ORIGINS[:2])"
        )
        self.assertEqual(
            set(output.strip().splitlines()[-1].split()),
            {self.config["app_url"], self.config["api_url"]},
            "DEV_MODE must retain HTTPS canonical application URLs.",
        )
        self.base_driver.get(https_url)
        self.assertIn("OpenWISP", self.base_driver.title)

    def test_redis_tls_certificate_policy(self):
        for dev_mode, expected_certificate_requirement in (
            ("False", "True"),
            ("True", "False"),
        ):
            with self.subTest(dev_mode=dev_mode):
                output, _ = self._execute_django_shell_command(
                    "import ssl; from django.conf import settings; "
                    "print(settings.CELERY_BROKER_USE_SSL['ssl_cert_reqs'] "
                    "== ssl.CERT_REQUIRED)",
                    environment={
                        "DEV_MODE": dev_mode,
                        "REDIS_USE_TLS": "True",
                    },
                )
                self.assertEqual(
                    output.strip().splitlines()[-1],
                    expected_certificate_requirement,
                )

    def test_redis_buckets_are_separated(self):
        output, _ = self._execute_django_shell_command(
            "from django.conf import settings; "
            "print(settings.SESSION_CACHE_ALIAS, "
            "settings.CACHES['default']['LOCATION'], "
            "settings.CACHES['sessions']['LOCATION'], "
            "settings.CHANNEL_LAYERS['default']['CONFIG']['hosts'][0]['address'], "
            "settings.CELERY_BROKER_URL, "
            "settings.CACHES['default']['OPTIONS'].get('PASSWORD'), "
            "settings.CACHES['sessions']['OPTIONS'].get('PASSWORD'))",
            environment={"REDIS_PASS": "test-password"},
        )
        values = output.strip().splitlines()[-1].split()
        self.assertEqual(
            values[0],
            "sessions",
        )
        self.assertEqual(
            [urlsplit(value).path for value in values[1:5]],
            ["/0", "/1", "/3", "/2"],
            "Django cache, sessions, Channels and Celery must use distinct "
            "Redis buckets.",
        )
        self.assertEqual(
            values[5:],
            ["test-password", "test-password"],
            "Django cache and sessions must use the configured Redis password.",
        )

    def test_custom_static_files_loaded(self):
        self.login()
        self.open(self.reverse_url("admin:index"))
        favicon_href = self.web_driver.find_element(
            By.CSS_SELECTOR, 'link[rel="icon"]'
        ).get_attribute("href")
        self.assertRegex(
            favicon_href,
            r"/static/ui/openwisp/images/favicon(\.[0-9a-f]+)?\.svg$",
        )
        value = self.web_driver.execute_script(
            "return getComputedStyle(document.body)"
            ".getPropertyValue('--openwisp-test');"
        )
        self.assertEqual(value.strip(), self.custom_static_token)

    def test_nginx_serves_precompressed_static_files(self):
        script = Path(__file__).parent / "scripts" / "precompress_static.py"
        path = "/opt/openwisp/static/precompressed-static.txt"
        custom_nginx_directory = Path(self.root_location) / "customization" / "nginx"
        custom_static_directory = custom_nginx_directory / "static"
        custom_path = custom_static_directory / "precompressed-static.txt"
        custom_assets = {
            "br": (
                b"\x1b \x00\xf8\x8dT\xb5\xbf\x1ek\x83\x93\x93 eoI\x08#\xb5\xf4\x15\x94"
                b"\xccc\x12\\"
                b"\xc7\xe6\xa1\xec\x01"
            ),
            "gzip": (
                b"\x1f\x8b\x08\x00\x00\x00\x00\x00\x02\xffK.-.\xc9\xcfU((JM"
                b"\xce\xcf\x05\x92"
                b"\xc5\xc5\xa9)\n\xc5%\x89%\x99\xc9\n\x89@N\t"
                b"\x00i\xf5y\x8e!\x00\x00\x00"
            ),
        }
        custom_files = {
            custom_path: b"custom static asset",
            Path(f"{custom_path}.br"): custom_assets["br"],
            Path(f"{custom_path}.gz"): custom_assets["gzip"],
        }
        original_custom_files = {
            file_path: file_path.read_bytes() if file_path.exists() else None
            for file_path in custom_files
        }
        custom_nginx_directory_existed = custom_nginx_directory.exists()
        custom_static_directory_existed = custom_static_directory.exists()
        self._execute_docker_compose_command(
            [
                "docker",
                "compose",
                "run",
                "--rm",
                "--no-deps",
                "--volume",
                f"{script}:/test_precompress_static.py:ro",
                "--entrypoint",
                "python",
                "dashboard",
                "/test_precompress_static.py",
            ]
        )
        try:
            app_url = urlsplit(self.live_server_url)
            static_url = urlunsplit(
                ("https", app_url.netloc, "/static/precompressed-static.txt", "", "")
            )

            def assert_precompressed_assets(expected_assets, location):
                for scheme in ("http", "https"):
                    url = static_url.replace("https", scheme, 1)
                    for encoding in ("br", "gzip"):
                        with self.subTest(
                            location=location, scheme=scheme, encoding=encoding
                        ):
                            request_info = request.Request(
                                url,
                                headers={"Accept-Encoding": encoding},
                            )
                            with request.urlopen(
                                request_info, context=self.ctx, timeout=10
                            ) as response:
                                self.assertEqual(
                                    response.getcode(),
                                    200,
                                    "Nginx must serve precompressed static files.",
                                )
                                self.assertEqual(
                                    response.headers.get("Content-Encoding"),
                                    encoding,
                                    "Nginx must honor the requested static file "
                                    "encoding.",
                                )
                                self.assertEqual(
                                    response.read(),
                                    expected_assets[encoding],
                                    "Nginx must serve the precompressed asset, "
                                    "not its fallback.",
                                )

            assert_precompressed_assets(
                {
                    "br": ASSETS[f"{custom_path.name}.br"],
                    "gzip": ASSETS[f"{custom_path.name}.gz"],
                },
                "shared",
            )
            custom_static_directory.mkdir(parents=True, exist_ok=True)
            for file_path, content in custom_files.items():
                file_path.write_bytes(content)
            assert_precompressed_assets(custom_assets, "custom")
        finally:
            for file_path, content in original_custom_files.items():
                if content is None:
                    file_path.unlink(missing_ok=True)
                else:
                    file_path.write_bytes(content)
            if not custom_static_directory_existed and custom_static_directory.exists():
                custom_static_directory.rmdir()
            if not custom_nginx_directory_existed and custom_nginx_directory.exists():
                custom_nginx_directory.rmdir()
            self._execute_docker_compose_command(
                [
                    "docker",
                    "compose",
                    "exec",
                    "-T",
                    "dashboard",
                    "rm",
                    "-f",
                    path,
                    f"{path}.br",
                    f"{path}.gz",
                ]
            )

    def test_device_monitoring_charts(self):
        self.login()
        self.get_resource("test-device", "admin:config_device_changelist")
        self.find_element(By.CSS_SELECTOR, "ul.tabs li.charts").click()
        try:
            WebDriverWait(self.base_driver, 3).until(EC.alert_is_present())
        except TimeoutException:
            # No alert means that the request to fetch
            # monitoring charts was successful.
            pass
        else:
            # When the request to fetch monitoring charts fails,
            # an error is shown.
            self.fail("An alert was found on the device chart page.")

    def test_default_topology(self):
        self.login()
        self.get_resource(
            "test-device",
            "admin:topology_topology_changelist",
            select_field="field-label",
        )

    def test_websocket_marker(self):
        """Ensure location marker updates are sent to another browser session."""
        cls = type(self)
        for driver in (cls.base_driver, cls.second_driver):
            try:
                driver.quit()
            except Exception:
                pass
        if self.config["driver"] == "firefox":
            cls.base_driver = self.get_firefox_webdriver()
            cls.second_driver = self.get_firefox_webdriver()
        if self.config["driver"] == "chromium":
            cls.base_driver = self.get_chrome_webdriver()
            cls.second_driver = self.get_chrome_webdriver()
        cls.web_driver = cls.base_driver
        location_name = "automated-websocket-selenium-loc01"

        def dismiss_location_alert():
            try:
                alert = WebDriverWait(self.second_driver, 5).until(
                    EC.alert_is_present()
                )
            except TimeoutException:
                return
            if "Could not find any address related to this location." in alert.text:
                alert.accept()

        def add_location_point():
            self.get_resource(
                location_name,
                "admin:geo_location_changelist",
                driver=self.second_driver,
            )
            self.find_element(By.NAME, "is_mobile", driver=self.second_driver).click()
            dismiss_location_alert()
            self.find_element(
                By.CLASS_NAME,
                "leaflet-draw-draw-marker",
                driver=self.second_driver,
            ).click()
            self.find_element(
                By.ID, "id_geometry-map", driver=self.second_driver
            ).click()
            self.find_element(By.NAME, "is_mobile", driver=self.second_driver).click()
            dismiss_location_alert()
            geometry = json.loads(
                self.find_element(
                    By.ID,
                    "id_geometry",
                    driver=self.second_driver,
                    wait_for="presence",
                ).get_attribute("value")
            )
            self._click_save_btn(self.second_driver)
            return geometry

        self._execute_django_shell_command(
            "from openwisp_controller.geo.models import Location; "
            "from openwisp_users.models import Organization; "
            f"Location.objects.filter(name={location_name!r}).delete(); "
            f"Location.objects.create(name={location_name!r}, type='outdoor', "
            "is_mobile=True, organization=Organization.objects.get(slug='default'))"
        )
        try:
            self.login()
            self.login(driver=self.second_driver)
            self.get_resource(location_name, "admin:geo_location_changelist")
            self.get_resource(
                location_name,
                "admin:geo_location_changelist",
                driver=self.second_driver,
            )
            self.assertEqual(
                self.find_element(
                    By.ID,
                    "id_geometry",
                    driver=self.base_driver,
                    wait_for="presence",
                ).get_attribute("value"),
                "",
            )
            geometry = add_location_point()

            def geometry_updated(driver):
                value = driver.find_element(By.ID, "id_geometry").get_attribute("value")
                return bool(value) and json.loads(value) == geometry

            try:
                WebDriverWait(self.base_driver, 10).until(geometry_updated)
            except TimeoutException:
                self.fail(
                    "Location geometry update was not received by the first browser."
                )
        finally:
            self._execute_django_shell_command(
                "from openwisp_controller.geo.models import Location; "
                f"Location.objects.filter(name={location_name!r}).delete()"
            )

    def test_topology_graph(self):
        """Ensure the admin graph visualizer renders database-backed topology data."""
        cls = type(self)
        cls.base_driver.quit()
        if self.config["driver"] == "firefox":
            cls.base_driver = self.get_firefox_webdriver()
        if self.config["driver"] == "chromium":
            cls.base_driver = self.get_chrome_webdriver()
        cls.web_driver = cls.base_driver
        label = "automated-selenium-test-02"

        def delete_topology():
            self._execute_django_shell_command(
                "from openwisp_network_topology.models import Topology; "
                f"Topology.objects.filter(label={label!r}).delete()"
            )

        fixture = (Path(__file__).parent / "static" / "network-graph.json").read_text()
        self.addCleanup(delete_topology)
        output, _ = self._execute_django_shell_command(
            "from openwisp_network_topology.models import Topology; "
            "from openwisp_users.models import Organization; "
            f"Topology.objects.filter(label={label!r}).delete(); "
            f"data = {fixture!r}; "
            f"topology = Topology(label={label!r}, "
            "parser='netdiff.NetJsonParser', strategy='receive', "
            "organization=Organization.objects.get(slug='default')); "
            "topology.full_clean(); topology.save(); "
            "graph = topology.get_topology_data(data); "
            "topology.update_topology(topology.diff(graph)); print(topology.pk)"
        )
        topology_url = self.reverse_url(
            "admin:topology_topology_change",
            {"object_id": output.strip().splitlines()[-1]},
        )
        self.login()
        self.open(topology_url)
        self.find_element(By.CSS_SELECTOR, "input.visualizelink").click()
        self.find_element(By.CSS_SELECTOR, "button.sideBarHandle").click()
        values = self.find_elements(By.CSS_SELECTOR, ".njg-valueLabel")
        self.assertEqual(
            [value.text.lower() for value in values],
            [label, "olsrv2", "0.14.1-1", "ff_dat_metric", "23", "18"],
        )
        self.assertEqual([], self.console_error_check())

    def test_create_prefix_users(self):
        """Ensure RADIUS prefix batches generate downloadable credentials."""
        batch_name = "automated-prefix-test-01"

        def delete_batch():
            self._execute_django_shell_command(
                "from openwisp_radius.models import RadiusBatch; "
                f"RadiusBatch.objects.filter(name={batch_name!r}).delete()"
            )

        self.login()
        self.open(self.reverse_url("admin:openwisp_radius_radiusbatch_add"))
        self.find_element(By.NAME, "strategy").find_element(
            By.XPATH, '//option[@value="prefix"]'
        ).click()
        self.find_element(By.NAME, "organization").find_element(
            By.XPATH, '//option[text()="default"]'
        ).click()
        self.find_element(By.NAME, "name").send_keys(batch_name)
        self.find_element(By.NAME, "prefix").send_keys("automated-prefix")
        self.find_element(By.NAME, "number_of_users").send_keys("1")
        self._click_save_btn()
        self.addCleanup(delete_batch)
        self.get_resource(batch_name, "admin:openwisp_radius_radiusbatch_changelist")
        credentials_url = self.base_driver.find_element(
            By.XPATH, '//a[text()="Download User Credentials"]'
        ).get_property("href")
        cookies = {
            cookie["name"]: cookie["value"] for cookie in self.base_driver.get_cookies()
        }
        request_info = request.Request(
            credentials_url,
            headers={
                "Cookie": "; ".join(
                    f"{name}={value}" for name, value in cookies.items()
                )
            },
        )
        try:
            response = request.urlopen(request_info, context=self.ctx, timeout=10)
        except (urlerror.HTTPError, OSError, ConnectionResetError) as error:
            self.fail(f"Cannot download PDF file: {error}")
        self.assertEqual(response.getcode(), 200)
        self.assertEqual(response.headers.get_content_type(), "application/pdf")
        self.assertEqual(response.read(4), b"%PDF")

    def test_console_errors(self):
        """Ensure key account and admin pages have no browser console errors."""
        view_names = [
            "admin:index",
            "account_reset_password",
            "admin:config_device_add",
            "admin:config_template_add",
            "admin:openwisp_radius_radiuscheck_add",
            "admin:openwisp_radius_radiusgroup_add",
            "admin:openwisp_radius_radiusbatch_add",
            "admin:openwisp_radius_nas_add",
            "admin:openwisp_radius_radiusreply_changelist",
            "admin:geo_floorplan_add",
            "admin:topology_link_add",
            "admin:topology_node_add",
            "admin:topology_topology_add",
            "admin:pki_ca_add",
            "admin:pki_cert_add",
            "admin:openwisp_users_user_add",
            "admin:firmware_upgrader_build_changelist",
            "admin:firmware_upgrader_build_add",
            "admin:firmware_upgrader_category_changelist",
            "admin:firmware_upgrader_category_add",
        ]
        change_form_list = [
            ["users", "admin:openwisp_radius_radiusgroup_changelist"],
            ["default-management-vpn", "admin:config_template_changelist"],
            ["default", "admin:config_vpn_changelist"],
            ["default", "admin:pki_ca_changelist"],
            ["default", "admin:pki_cert_changelist"],
            ["default", "admin:openwisp_users_organization_changelist"],
            [
                "test_superuser2",
                "admin:openwisp_users_user_changelist",
                "field-username",
            ],
        ]
        self.login()
        self.create_superuser("sample@email.com", "test_superuser2")
        for view_name in view_names:
            with self.subTest(view_name=view_name):
                self.open(self.reverse_url(view_name))
                self.assertEqual([], self.console_error_check())
                self.assertIn("OpenWISP", self.base_driver.title)
        for change_form in change_form_list:
            with self.subTest(resource=change_form[0], path=change_form[1]):
                self.get_resource(*change_form)
                self.assertEqual([], self.console_error_check())
                self.assertIn("OpenWISP", self.base_driver.title)

    def test_add_superuser(self):
        """Create new user to ensure a new user can be added."""
        self.login()
        self.create_superuser()
        self.assertEqual(
            "The user “test_superuser” was changed successfully.",
            self.find_element(By.CLASS_NAME, "success").text,
        )

    def test_forgot_password(self):
        """Test forgot password to ensure that postfix is working properly."""

        self.login()
        self.logout()
        logout_title = self.find_element(
            By.CSS_SELECTOR, ".title-wrapper h1", timeout=3, wait_for="presence"
        )
        self.assertEqual(logout_title.text, "Logged out", "Logout failed.")
        self.open(self.reverse_url("account_reset_password"))
        self.find_element(By.NAME, "email").send_keys("admin@example.com")
        self.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        self._wait_until_page_ready()
        self.assertIn(
            "We have sent you an email. If you have not received "
            "it please check your spam folder. Otherwise contact us "
            "if you do not receive it in a few minutes.",
            self.base_driver.page_source,
        )

    def test_celery(self):
        """Ensure celery and celery-beat tasks are registered."""
        expected_output_list = [
            "openwisp.tasks.radius_tasks",
            "openwisp.tasks.save_snapshot",
            "openwisp.tasks.update_topology",
            "openwisp_controller.config.tasks.change_devices_templates",
            "openwisp_controller.config.tasks.create_vpn_dh",
            "openwisp_controller.config.tasks.invalidate_devicegroup_cache_change",
            "openwisp_controller.config.tasks.invalidate_devicegroup_cache_delete",
            "openwisp_controller.config.tasks.invalidate_vpn_server_devices_cache_change",  # noqa: E501
            "openwisp_controller.config.tasks.trigger_vpn_server_endpoint",
            "openwisp_controller.config.tasks.update_template_related_config_status",
            "openwisp_controller.connection.tasks.auto_add_credentials_to_devices",
            "openwisp_controller.connection.tasks.launch_command",
            "openwisp_controller.connection.tasks.update_config",
            "openwisp_controller.subnet_division.tasks.provision_extra_ips",
            "openwisp_controller.subnet_division.tasks.provision_subnet_ip_for_existing_devices",  # noqa: E501
            "openwisp_controller.subnet_division.tasks.update_subnet_division_index",
            "openwisp_controller.subnet_division.tasks.update_subnet_name_description",
            "openwisp_firmware_upgrader.tasks.batch_upgrade_operation",
            "openwisp_firmware_upgrader.tasks.create_all_device_firmwares",
            "openwisp_firmware_upgrader.tasks.create_device_firmware",
            "openwisp_firmware_upgrader.tasks.upgrade_firmware",
            "openwisp_monitoring.check.tasks.auto_create_check",
            "openwisp_monitoring.check.tasks.perform_check",
            "openwisp_monitoring.check.tasks.run_checks",
            "openwisp_monitoring.device.tasks.delete_wifi_clients_and_sessions",
            "openwisp_monitoring.device.tasks.offline_device_close_session",
            "openwisp_monitoring.device.tasks.trigger_device_checks",
            "openwisp_monitoring.device.tasks.write_device_metrics",
            "openwisp_monitoring.device.tasks.handle_disabled_organization",
            "openwisp_monitoring.monitoring.tasks.delete_timeseries",
            "openwisp_monitoring.monitoring.tasks.migrate_timeseries_database",
            "openwisp_monitoring.monitoring.tasks.timeseries_batch_write",
            "openwisp_monitoring.monitoring.tasks.timeseries_write",
            "openwisp_notifications.tasks.delete_ignore_object_notification",
            "openwisp_notifications.tasks.delete_notification",
            "openwisp_notifications.tasks.delete_obsolete_objects",
            "openwisp_notifications.tasks.delete_old_notifications",
            "openwisp_notifications.tasks.ns_organization_created",
            "openwisp_notifications.tasks.ns_organization_user_deleted",
            "openwisp_notifications.tasks.ns_register_unregister_notification_type",
            "openwisp_notifications.tasks.update_org_user_notificationsetting",
            "openwisp_radius.tasks.cleanup_stale_radacct",
            "openwisp_radius.tasks.convert_called_station_id",
            "openwisp_radius.tasks.delete_old_postauth",
            "openwisp_radius.tasks.delete_old_radacct",
            "openwisp_radius.tasks.delete_old_radiusbatch_users",
            "openwisp_radius.tasks.delete_unverified_users",
            "openwisp_radius.tasks.perform_change_of_authorization",
            "openwisp_radius.tasks.send_login_email",
            "openwisp_users.tasks.deactivate_expired_users",
            "openwisp_users.tasks.expiration_reminder_email",
            "openwisp_users.tasks.password_expiration_email",
        ]
        output, _ = self._execute_django_shell_command(
            "from django.conf import settings; print(settings.EMAIL_BACKEND)"
        )
        if (
            output.strip().splitlines()[-1]
            == "djcelery_email.backends.CeleryEmailBackend"
        ):
            expected_output_list.insert(0, "djcelery_email_send_multiple")

        def _test_celery_task_registered(container_name):
            container_id = self.docker_compose_get_container_id(container_name)
            celery_container = self.docker_client.containers.get(container_id)
            result = celery_container.exec_run("celery -A openwisp inspect registered")
            self.assertEqual(result.exit_code, 0)

            output = result.output.decode("utf-8")
            for expected_output in expected_output_list:
                if expected_output not in output:
                    self.fail(
                        "Not all celery / celery-beat tasks are registered.\n"
                        f"Expected celery task not found:\n{expected_output}"
                    )

        with self.subTest("Test celery container"):
            _test_celery_task_registered("celery")

        with self.subTest("Test celery_monitoring container"):
            _test_celery_task_registered("celery_monitoring")

    def test_celery_beat_schedule_without_radius(self):
        """Ensure user expiration tasks are scheduled without RADIUS."""
        output, _ = self._execute_django_shell_command(
            (
                "from openwisp.celery import app; "
                "print('\\n'.join(entry['task'] "
                "for entry in app.conf.beat_schedule.values() "
                "if entry['task'].startswith('openwisp_users.')))"
            ),
            environment={"USE_OPENWISP_RADIUS": "False"},
        )
        self.assertIn("openwisp_users.tasks.deactivate_expired_users", output)
        self.assertIn("openwisp_users.tasks.expiration_reminder_email", output)
        output, _ = self._execute_django_shell_command(
            "from django.conf import settings; "
            "from openwisp.celery import app; "
            "print(settings.TIME_ZONE, app.conf.timezone)"
        )
        self.assertEqual(*output.strip().splitlines()[-1].split())

    def test_radius_user_registration(self):
        """Ensure users can register using the RADIUS API."""
        registration_url = self.reverse_url("radius:rest_register", {"slug": "default"})
        url = f"{self.config['api_url']}{registration_url}"
        username = "signup-user"
        try:
            response = requests.post(
                url,
                json={
                    "username": username,
                    "email": "user@signup.com",
                    "password1": "rLx6OH%[",
                    "password2": "rLx6OH%[",
                },
                verify=False,
                timeout=10,
            )
            self.assertEqual(response.status_code, 201, response.text)
        finally:
            self.delete_test_users(username)

    def test_freeradius(self):
        """Ensure freeradius service is working correctly."""
        token_url = self.reverse_url("radius:user_auth_token", {"slug": "default"})
        token_page = f"{self.config['api_url']}{token_url}"
        request_body = "username=admin&password=admin".encode("utf-8")
        request_info = request.Request(token_page, data=request_body)
        try:
            response = request.urlopen(request_info, context=self.ctx)
        except (urlerror.HTTPError, OSError, ConnectionResetError):
            self.fail(f"Couldn't get radius-token, check {self.config['api_url']}")
        self.assertIn('"is_active":true', response.read().decode())

        container_id = self.docker_compose_get_container_id("freeradius")
        freeradius_container = self.docker_client.containers.get(container_id)
        freeradius_container.exec_run("apk add freeradius freeradius-radclient")
        result = freeradius_container.exec_run(
            "radtest admin admin localhost 0 testing123"
        )
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Received Access-Accept", result.output.decode("utf-8"))

        remove_tainted_container = [
            "docker compose rm -sf freeradius",
            "docker compose up -d freeradius",
        ]
        for command in remove_tainted_container:
            subprocess.Popen(
                command.split(),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=self.root_location,
            ).communicate()

    def test_containers_down(self):
        """Ensure Compose succeeds and no container has stopped."""
        cmd = subprocess.Popen(
            ["docker", "compose", "ps"],
            universal_newlines=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.root_location,
        )
        output, error = cmd.communicate()
        self.assertEqual(cmd.returncode, 0, error)
        if "Exit" in output:
            self.fail(
                f"One of the containers is down!\nOutput:\n{output}\nError:\n{error}"
            )


class TestLocalUtils(BaseTestUtils, unittest.TestCase):
    """Tests for local utilities"""

    def test_profile_configures_shell_defaults_and_preserves_overrides(self):
        for dev_mode, settings, expected in (
            (
                "True",
                {},
                "True False False",
            ),
            (
                "True",
                {
                    "NGINX_HTTP_ALLOW": "False",
                    "OPENWISP_GEOCODING_CHECK": "True",
                    "FREERADIUS_DEBUG_MODE": "True",
                },
                "False True True",
            ),
            (
                "False",
                {},
                "False True False",
            ),
        ):
            with self.subTest(dev_mode=dev_mode, settings=settings):
                environment = os.environ.copy()
                for variable in (
                    "NGINX_HTTP_ALLOW",
                    "OPENWISP_GEOCODING_CHECK",
                    "FREERADIUS_DEBUG_MODE",
                ):
                    environment.pop(variable, None)
                environment["DEV_MODE"] = dev_mode
                environment.update(settings)
                result = subprocess.run(
                    [
                        "bash",
                        "-c",
                        "source images/common/utils.sh; "
                        "configure_dev_mode; "
                        'printf "%s %s %s" '
                        '"$NGINX_HTTP_ALLOW" "$OPENWISP_GEOCODING_CHECK" '
                        '"$FREERADIUS_DEBUG_MODE"',
                    ],
                    cwd=self.root_location,
                    check=False,
                    capture_output=True,
                    text=True,
                    env=environment,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, expected)

    def test_curl_download_uses_the_profile_tls_policy(self):
        for dev_mode, expected_arguments in (
            ("False", "--silent https://example.com"),
            ("True", "--insecure --silent https://example.com"),
        ):
            with self.subTest(dev_mode=dev_mode):
                environment = os.environ.copy()
                environment["DEV_MODE"] = dev_mode
                result = subprocess.run(
                    [
                        "bash",
                        "-c",
                        "source images/common/utils.sh; "
                        'curl() { printf "%s" "$*"; }; '
                        "curl_download --silent https://example.com",
                    ],
                    cwd=self.root_location,
                    check=False,
                    capture_output=True,
                    text=True,
                    env=environment,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, expected_arguments)

    def test_freeradius_debug_mode_is_independent(self):
        repository_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            (tmpdir / "init_command.sh").write_text(
                (repository_root / "images" / "common" / "init_command.sh").read_text()
            )
            (tmpdir / "utils.sh").write_text(
                "init_conf() { :; }\nwait_nginx_services() { :; }\n"
            )
            (tmpdir / "docker-entrypoint.sh").write_text('printf "%s" "$*"\n')
            environment = os.environ.copy()
            environment.update(
                {
                    "DEBUG_MODE": "True",
                    "MODULE_NAME": "freeradius",
                    "PATH": f"{tmpdir}:{environment['PATH']}",
                }
            )
            for freeradius_debug_mode, expected in (("False", ""), ("True", "-X")):
                with self.subTest(freeradius_debug_mode=freeradius_debug_mode):
                    environment["FREERADIUS_DEBUG_MODE"] = freeradius_debug_mode
                    result = subprocess.run(
                        ["bash", "init_command.sh"],
                        cwd=tmpdir,
                        check=False,
                        capture_output=True,
                        text=True,
                        env=environment,
                    )
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stdout, expected)

    def test_nginx_development_headers_clear_hsts(self):
        repository_root = Path(__file__).resolve().parents[1]
        header_file = (
            repository_root / "images" / "openwisp_nginx" / "openwisp.security.dev.conf"
        )
        self.assertEqual(
            header_file.read_text().strip(),
            'add_header Strict-Transport-Security "max-age=0" always;',
        )
        utils = (repository_root / "images" / "common" / "utils.sh").read_text()
        self.assertIn("if is_dev_mode; then", utils)
        self.assertIn("header_file=/etc/nginx/openwisp.security.dev.conf", utils)
        for template in (
            "openwisp.ssl.template.conf",
            "openwisp.template.conf",
        ):
            with self.subTest(template=template):
                content = (
                    repository_root / "images" / "openwisp_nginx" / template
                ).read_text()
                self.assertIn("include $NGINX_SECURITY_HEADERS_FILE;", content)

    def test_workflows_publish_to_gitlab_registry(self):
        repository_root = Path(__file__).resolve().parents[1]
        registry = "registry.gitlab.com/openwisp/docker-openwisp"
        ci_workflow = (repository_root / ".github" / "workflows" / "ci.yml").read_text()
        release_workflow = (
            repository_root / ".github" / "workflows" / "release.yml"
        ).read_text()
        self.assertIn(
            f"make publish USER={registry} TAG=edge SKIP_BUILD=true SKIP_TESTS=true",
            ci_workflow,
        )
        self.assertIn(
            f"make release USER={registry} SKIP_BUILD=true",
            release_workflow,
        )

    @contextmanager
    def _makefile_test_environment(self):
        """Yield an isolated Makefile runner, Docker command log, and environment.

        The temporary directory uses a copied Makefile and a mock Docker
        command, allowing tests to assert Makefile behavior without
        executing Docker. Its contents are removed when the context exits.
        """
        repository_root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            bin_directory = tmpdir / "bin"
            bin_directory.mkdir()
            docker_log = tmpdir / "docker.log"
            docker_command = bin_directory / "docker"
            docker_command.write_text(
                "#!/bin/bash\n"
                'printf "%s\\n" "$*" >> "$DOCKER_LOG"\n'
                'if [ "$1" = "$FAIL_COMMAND" ]; then\n'
                "    exit 1\n"
                "fi\n"
            )
            docker_command.chmod(0o755)
            (tmpdir / "Makefile").write_text((repository_root / "Makefile").read_text())
            (tmpdir / ".env").write_text("")
            environment = os.environ.copy()
            environment["DOCKER_LOG"] = str(docker_log)
            environment["PATH"] = f"{bin_directory}:{environment['PATH']}"

            def run_make(*arguments):
                return subprocess.run(
                    ["make", *arguments],
                    cwd=tmpdir,
                    check=False,
                    capture_output=True,
                    text=True,
                    env=environment,
                )

            yield run_make, docker_log, environment

    def test_make_start_rejects_development_mode(self):
        with self._makefile_test_environment() as (run_make, docker_log, _):
            docker_log.write_text("")
            for dev_mode in ("True", "true", "TRUE", "Yes", "yes", "YES"):
                with self.subTest(dev_mode=dev_mode):
                    development_start = run_make("start", f"DEV_MODE={dev_mode}")
                    self.assertNotEqual(development_start.returncode, 0)
                    self.assertIn("Set DEV_MODE=False", development_start.stdout)
                    self.assertEqual(docker_log.read_text(), "")

    def test_makefile_pulls_from_docker_hub_and_fails_on_image_command_error(self):
        """Verify Docker Hub pulls and Makefile command failure propagation."""
        with self._makefile_test_environment() as (run_make, docker_log, environment):
            pull = run_make("pull", "OPENWISP_VERSION=25.10.4")
            self.assertEqual(pull.returncode, 0, pull.stderr)
            commands = docker_log.read_text().splitlines()
            self.assertEqual(
                len(commands), 18, "The Makefile must pull and tag all images."
            )
            self.assertTrue(
                all(
                    command.startswith("pull --quiet docker.io/openwisp/")
                    for command in commands[::2]
                ),
                "The default pull registry must be Docker Hub.",
            )

            for command in ("pull", "tag"):
                with self.subTest(target="pull", command=command):
                    environment["FAIL_COMMAND"] = command
                    failed_pull = run_make("pull", "OPENWISP_VERSION=25.10.4")
                    self.assertNotEqual(
                        failed_pull.returncode,
                        0,
                        f"A failed image {command} must fail make pull.",
                    )

            environment.pop("FAIL_COMMAND")
            docker_log.write_text("")
            publish_arguments = (
                "publish",
                "USER=docker.io/openwisp",
                "TAG=25.10.4",
                "OPENWISP_VERSION=25.10.4",
                "SKIP_BUILD=true",
                "SKIP_TESTS=true",
            )
            publish = run_make(*publish_arguments)
            self.assertEqual(publish.returncode, 0, publish.stderr)
            self.assertFalse(
                any(
                    command.startswith("rmi ")
                    for command in docker_log.read_text().splitlines()
                ),
                "Publishing must retain the source tags for another registry.",
            )

            for command in ("tag", "push"):
                with self.subTest(target="publish", command=command):
                    environment["FAIL_COMMAND"] = command
                    failed_publish = run_make(*publish_arguments)
                    self.assertNotEqual(
                        failed_publish.returncode,
                        0,
                        f"A failed image {command} must fail make publish.",
                    )

    def test_update_version_updates_only_version_file(self):
        """Verify version updates and rejected legacy bump commands."""
        repository_root = Path(__file__).resolve().parents[1]
        makefile_content = (
            "RELEASE_VERSION = $(shell cat images/common/openwisp/VERSION)\n"
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            version_file = tmpdir / "images" / "common" / "openwisp" / "VERSION"
            version_file.parent.mkdir(parents=True)
            version_file.write_text("25.10.3\n")
            makefile = tmpdir / "Makefile"
            makefile.write_text((repository_root / "Makefile").read_text())
            (tmpdir / ".env").write_text("")
            (tmpdir / "build.py").write_text((repository_root / "build.py").read_text())

            with self.subTest(command="bump with version"):
                result = subprocess.run(
                    ["make", "bump", "VERSION=26.01.0"],
                    cwd=tmpdir,
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(version_file.read_text(), "26.01.0\n")
                self.assertIn(makefile_content, makefile.read_text())
                self.assertFalse((version_file.parent / "_version.py").exists())

            with self.subTest(command="bump without version"):
                missing_argument = subprocess.run(
                    ["make", "bump"],
                    cwd=tmpdir,
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertNotEqual(missing_argument.returncode, 0)

            with self.subTest(command="legacy bump-version"):
                old_target = subprocess.run(
                    ["make", "bump-version"],
                    cwd=tmpdir,
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertNotEqual(old_target.returncode, 0)

    def test_auto_install_argument_parsing(self):
        script = Path(self.root_location) / "deploy" / "auto-install.sh"
        command = (
            "source <(sed '/^## Init script$/,$d' \"$AUTO_INSTALL_SCRIPT\"); "
            'printf "%s|%s" "$action" "$USER_INSTALL_PATH"'
        )
        environment = os.environ.copy()
        environment["AUTO_INSTALL_SCRIPT"] = str(script)
        cases = (
            (
                ("--install", "/srv/openwisp installation"),
                "install|/srv/openwisp installation",
            ),
            (
                ("--upgrade", "/srv/openwisp installation"),
                "upgrade|/srv/openwisp installation",
            ),
            (("--upgrade", "--help"), "help|/opt/openwisp"),
        )
        for arguments, expected in cases:
            with self.subTest(arguments=arguments):
                result = subprocess.run(
                    ["bash", "-c", command, "auto-install.sh", *arguments],
                    check=False,
                    capture_output=True,
                    text=True,
                    env=environment,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, expected)


class TestOpenVPN(unittest.TestCase):
    def test_crl_refresh_detects_revocation_changes(self):
        """Ensure CRL metadata updates do not trigger a revocation change."""
        script = Path(__file__).parent / "scripts" / "openvpn.sh"
        image = os.environ.get("OPENWISP_TEST_OPENVPN_IMAGE")
        name = f"openvpn-test-{os.getpid()}-{time.time_ns()}"
        if not image:
            self.fail("OPENWISP_TEST_OPENVPN_IMAGE is required for OpenVPN tests.")
        try:
            result = subprocess.run(
                [
                    "docker",
                    "run",
                    "--rm",
                    "--name",
                    name,
                    "--volume",
                    f"{script}:/test_openvpn.sh:ro",
                    "--entrypoint",
                    "sh",
                    image,
                    "/test_openvpn.sh",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
        except subprocess.TimeoutExpired as error:
            # Remove the container if it is still running after the timeout.
            subprocess.run(
                ["docker", "rm", "--force", name],
                check=False,
                capture_output=True,
                text=True,
            )
            self.fail(
                f"OpenVPN test timed out:\n{error.stdout or ''}{error.stderr or ''}"
            )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
