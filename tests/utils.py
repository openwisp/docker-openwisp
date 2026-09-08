import json
import os
import ssl
import subprocess
from time import sleep

import docker
from openwisp_utils.tests import SeleniumTestMixin
from selenium.webdriver.common.by import By


class BaseTestUtils:
    """Base class for setting up test parameters and utilities."""

    docker_compose_timeout = 120
    docker_client = docker.from_env()
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    config_file = os.environ.get(
        "OPENWISP_TEST_CONFIG", os.path.join(os.path.dirname(__file__), "config.json")
    )
    root_location = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")
    _url_cache = {}
    with open(config_file) as json_file:
        config = json.load(json_file)

    def shortDescription(self):
        """Keep verbose unittest output focused on test names, not docstrings."""
        return None

    @classmethod
    def _execute_docker_compose_command(cls, cmd_args, use_text_mode=False):
        """Execute a docker compose command and log output."""
        kwargs = {
            "stdout": subprocess.PIPE,
            "stderr": subprocess.PIPE,
            "cwd": cls.root_location,
        }
        if use_text_mode:
            kwargs["text"] = True
        try:
            cmd = subprocess.run(
                cmd_args,
                check=False,
                timeout=cls.docker_compose_timeout,
                **kwargs,
            )
        except subprocess.TimeoutExpired as e:
            output = e.stdout or ""
            error = e.stderr or ""
            if isinstance(output, bytes):
                output = output.decode("utf-8", errors="replace") if output else ""
            if isinstance(error, bytes):
                error = error.decode("utf-8", errors="replace") if error else ""
            with open(cls.config["logs_file"], "a") as logs_file:
                logs_file.write(output)
                logs_file.write(error)
            raise RuntimeError(
                "docker compose command timed out "
                f"after {cls.docker_compose_timeout}s: {' '.join(cmd_args)}"
            )
        if use_text_mode:
            output, error = cmd.stdout, cmd.stderr
        else:
            output = cmd.stdout.decode("utf-8", errors="replace") if cmd.stdout else ""
            error = cmd.stderr.decode("utf-8", errors="replace") if cmd.stderr else ""
        with open(cls.config["logs_file"], "a") as logs_file:
            logs_file.write(output)
            logs_file.write(error)
        if cmd.returncode != 0:
            raise RuntimeError(
                f"docker compose command failed "
                f"({cmd.returncode}): {' '.join(cmd_args)}"
            )
        return output, error

    @classmethod
    def _execute_django_shell_command(
        cls, command, service="dashboard", environment=None
    ):
        cmd_args = ["docker", "compose", "exec", "-T"]
        for name, value in (environment or {}).items():
            cmd_args.extend(["-e", f"{name}={value}"])
        cmd_args.extend([service, "python", "manage.py", "shell", "-c", command])
        return cls._execute_docker_compose_command(cmd_args, use_text_mode=True)

    @classmethod
    def reverse_url(cls, view_name, kwargs=None):
        cache_key = (view_name, json.dumps(kwargs or {}, sort_keys=True))
        if cache_key in cls._url_cache:
            return cls._url_cache[cache_key]
        output, _ = cls._execute_django_shell_command(
            "from django.urls import reverse; "
            f"print(reverse({view_name!r}, kwargs={kwargs!r}))"
        )
        url = output.strip().splitlines()[-1]
        cls._url_cache[cache_key] = url
        return url

    def docker_compose_get_container_id(self, container_name):
        """Get the Docker container ID for a specific container.

        Parameters:

        - container_name (str): The name of the Docker container.

        Returns:
            str: The ID of the Docker container.
        """
        output, _ = self._execute_docker_compose_command(
            ["docker", "compose", "ps", "--quiet", container_name]
        )
        return output.rstrip()


class FunctionalTestUtils(SeleniumTestMixin, BaseTestUtils):
    """Utilities for functional testing."""

    test_usernames_to_delete = set()
    browser = "chrome"

    @classmethod
    def delete_test_users(cls, *usernames):
        """Delete test-created users without relying on browser state."""
        usernames = sorted(set(usernames))
        if not usernames:
            return
        cls._execute_django_shell_command(
            "from openwisp_users.models import User; "
            f"User.objects.filter(username__in={usernames!r}).delete()"
        )

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
        driver.execute_script("window.scrollTo(0, 0);")
        self.find_element(By.NAME, "_save", driver=driver).click()

    def create_superuser(
        self,
        email="test@user.com",
        username="test_superuser",
        password="randomPassword01!",
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
        self.open(self.reverse_url("admin:openwisp_users_user_add"), driver=driver)
        self.find_element(By.NAME, "username", driver=driver).send_keys(username)
        self.find_element(By.NAME, "email", driver=driver).send_keys(email)
        self.find_element(By.NAME, "password1", driver=driver).send_keys(password)
        self.find_element(By.NAME, "password2", driver=driver).send_keys(password)
        self.find_element(By.NAME, "is_superuser", driver=driver).click()
        self._click_save_btn(driver)
        self.test_usernames_to_delete.add(username)
        self._click_save_btn(driver)
        self._wait_until_page_ready()
        self.wait_for_visibility(By.ID, "content", driver=driver, timeout=10)

    def get_resource(
        self, resource_name, view_name, select_field="field-name", driver=None
    ):
        """Navigate to a resource's change form page.

        Parameters:

        - resource_name (str): The name of the resource to find.
        - view_name (str): The Django URL view name for the resource list.
        - select_field (str, optional): The field used to identify the
          resource. Defaults to 'field-name'.
        - driver (selenium.webdriver, optional): The Selenium WebDriver
          instance. Defaults to `self.base_driver`.
        """
        if not driver:
            driver = self.base_driver
        self.open(self.reverse_url(view_name), driver=driver)
        resources = self.find_elements(
            By.CLASS_NAME, select_field, wait_for="presence", driver=driver
        )
        for resource in resources:
            if len(resource.find_elements(By.LINK_TEXT, resource_name)):
                resource.find_element(By.LINK_TEXT, resource_name).click()
                break
        self._wait_until_page_ready()

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
            if logentry["level"] == "SEVERE":
                # Ignore error generated due to "leaflet" issue
                # https://github.com/makinacorpus/django-leaflet/pull/380
                if "leaflet" in logentry["message"]:
                    continue
                # Ignore error generated due to "beforeunload" chrome issue
                # https://stackoverflow.com/questions/10680544/beforeunload-chrome-issue
                if "beforeunload" in logentry["message"]:
                    continue
                console_logs.append(logentry["message"])
        return console_logs
