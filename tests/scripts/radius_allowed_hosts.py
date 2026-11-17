import importlib
import os
import unittest
from unittest import mock

import tldextract


class TestRadiusAllowedHosts(unittest.TestCase):
    def setUp(self):
        environment = mock.patch.dict(
            os.environ,
            {
                "USE_OPENWISP_RADIUS": "True",
                "DASHBOARD_DOMAIN": "dashboard.example.com",
                "API_DOMAIN": "api.example.com",
                "SSL_CERT_MODE": "False",
            },
        )
        environment.start()
        self.addCleanup(environment.stop)
        # Published images may still carry the old baked-in allowlist.
        os.environ.pop("OPENWISP_RADIUS_FREERADIUS_ALLOWED_HOSTS", None)
        os.environ.pop("DEFAULT_NETWORK_SUBNET", None)
        extractor = mock.patch.object(
            tldextract, "extract", tldextract.TLDExtract(suffix_list_urls=())
        )
        extractor.start()
        self.addCleanup(extractor.stop)

    def test_standalone_image_keeps_default_subnet(self):
        self.assertEqual(self._allowed_hosts(), ["172.18.0.0/16"])

    def test_configured_subnet_becomes_allowlist(self):
        os.environ["DEFAULT_NETWORK_SUBNET"] = "10.250.10.0/24"
        self.assertEqual(self._allowed_hosts(), ["10.250.10.0/24"])

    def test_explicit_allowlist_overrides_subnet(self):
        os.environ["DEFAULT_NETWORK_SUBNET"] = "10.250.10.0/24"
        os.environ["OPENWISP_RADIUS_FREERADIUS_ALLOWED_HOSTS"] = (
            "192.0.2.20,198.51.100.0/24"
        )
        self.assertEqual(
            self._allowed_hosts(),
            ["192.0.2.20", "198.51.100.0/24"],
        )

    def test_explicit_empty_allowlist_is_not_replaced(self):
        os.environ["DEFAULT_NETWORK_SUBNET"] = "10.250.10.0/24"
        os.environ["OPENWISP_RADIUS_FREERADIUS_ALLOWED_HOSTS"] = ""
        self.assertEqual(self._allowed_hosts(), [""])

    def _allowed_hosts(self):
        settings = importlib.import_module("openwisp.settings")
        return importlib.reload(settings).OPENWISP_RADIUS_FREERADIUS_ALLOWED_HOSTS


if __name__ == "__main__":
    unittest.main()
