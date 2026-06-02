import subprocess
import unittest
from pathlib import Path


class NginxConfigTest(unittest.TestCase):
    def _get_hsts_header(self, script):
        repository_root = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            ["bash", "-c", script],
            cwd=repository_root,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def test_hsts_is_disabled_by_default_with_self_signed_ssl(self):
        header = self._get_hsts_header(
            "source images/common/utils.sh; "
            "unset NGINX_HSTS_ENABLED; "
            "SSL_CERT_MODE=SelfSigned; "
            "configure_hsts_header; "
            'printf "%s" "$NGINX_HSTS_HEADER"'
        )

        self.assertEqual(header, "")

    def test_hsts_is_enabled_by_default_with_production_ssl(self):
        header = self._get_hsts_header(
            "source images/common/utils.sh; "
            "unset NGINX_HSTS_ENABLED; "
            "SSL_CERT_MODE=Yes; "
            "configure_hsts_header; "
            'printf "%s" "$NGINX_HSTS_HEADER"'
        )

        self.assertIn("Strict-Transport-Security", header)

    def test_hsts_can_be_disabled_explicitly(self):
        header = self._get_hsts_header(
            "source images/common/utils.sh; "
            "NGINX_HSTS_ENABLED=False; "
            "SSL_CERT_MODE=Yes; "
            "configure_hsts_header; "
            'printf "%s" "$NGINX_HSTS_HEADER"'
        )

        self.assertEqual(header, "")


if __name__ == "__main__":
    unittest.main()
