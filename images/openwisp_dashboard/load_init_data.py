"""Load initial data before starting the server.

- Create superuser `admin`.
- Create default CA
- Create default Cert
- Create default VPN
- Create default VPN Client Template
- Create default Credentials
- Create SSH Key template
"""

import json
import os

import django
import redis
import redis.exceptions
from openwisp.utils import env_bool

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "openwisp.settings")
django.setup()
from django.conf import settings  # noqa


def create_admin():
    """Creates superuser `admin` if it does not exist."""
    User.objects.filter(is_superuser=True).exists() or User.objects.create_superuser(
        "admin", "admin@example.com", "admin"
    )


def create_default_ca():
    """Create default certificate authority."""
    ca_name = os.environ["X509_NAME_CA"]
    if Ca.objects.filter(name=ca_name).exists():
        return Ca.objects.get(name=ca_name)

    ca = Ca(
        name=ca_name,
        country_code=os.environ["X509_COUNTRY_CODE"],
        state=os.environ["X509_STATE"],
        city=os.environ["X509_CITY"],
        organization_name=os.environ["X509_ORGANIZATION_NAME"],
        organizational_unit_name=os.environ["X509_ORGANIZATION_UNIT_NAME"],
        email=os.environ["X509_EMAIL"],
        common_name=os.environ["X509_COMMON_NAME"],
        notes=(
            "This CA was created during the setup, it is used for "
            "the default management VPN. Please do not rename it."
        ),
    )
    ca.full_clean()
    ca.save()
    return ca


def create_default_cert(ca):
    """Creates default certificate."""
    cert_name = os.environ["X509_NAME_CERT"]
    if Cert.objects.filter(name=cert_name).exists():
        return Cert.objects.get(name=cert_name)

    cert = Cert(
        ca=ca,
        name=cert_name,
        country_code=os.environ["X509_COUNTRY_CODE"],
        state=os.environ["X509_STATE"],
        city=os.environ["X509_CITY"],
        organization_name=os.environ["X509_ORGANIZATION_NAME"],
        organizational_unit_name=os.environ["X509_ORGANIZATION_UNIT_NAME"],
        email=os.environ["X509_EMAIL"],
        common_name=os.environ["X509_COMMON_NAME"],
        notes=(
            "This certificate was created during the setup. "
            "It is used for the default management VPN. "
            "Please do not rename it."
        ),
    )
    cert.full_clean()
    cert.save()
    return cert


def create_default_vpn(ca, cert):
    """Creates default vpn."""
    vpn_name = os.environ["VPN_NAME"]
    if Vpn.objects.exists():
        try:
            vpn = Vpn.objects.get(name=vpn_name)
        except Vpn.DoesNotExist:
            # The VPN name might be changed by the user,
            # in this scenario, return the first VPN object.
            vpn = Vpn.objects.first()
        if redis_client.get("openwisp_default_vpn_uuid"):
            # The VPN UUID and key has already been set in Redis.
            return vpn
    else:
        vpn = Vpn(
            ca=ca,
            cert=cert,
            name=vpn_name,
            notes=(
                "This is the default management VPN created during setup, "
                "you may modify these settings and they will soon reflect "
                "in your OpenVPN Server instance."
            ),
            host=os.environ["VPN_DOMAIN"],
            backend="openwisp_controller.vpn_backends.OpenVpn",
        )
        with open("openvpn.json", "r") as json_file:
            vpn.config = json.load(json_file)
        vpn.full_clean()
        vpn.save()

    redis_client.set("openwisp_default_vpn_uuid", str(vpn.id), ex=None)
    redis_client.set("openwisp_default_vpn_key", str(vpn.key), ex=None)
    redis_client.set("openwisp_default_vpn_ca_uuid", str(ca.id), ex=None)
    return vpn


def create_default_vpn_template(vpn):
    """Creates default vpn client template."""
    template_name = os.environ["VPN_CLIENT_NAME"]
    if Template.objects.filter(vpn=vpn).exists():
        return Template.objects.get(vpn=vpn)

    template = Template(
        auto_cert=True,
        name=template_name,
        type="vpn",
        tags="Management, VPN",
        backend="netjsonconfig.OpenWrt",
        vpn=vpn,
        default=True,
    )
    template.full_clean()
    template.config["openvpn"][0]["log"] = "/var/log/tun0.log"
    template.save()
    return template


def create_default_credentials():
    private_key_filepath = os.environ["SSH_PRIVATE_KEY_PATH"]
    if Credentials.objects.exists():
        return
    try:
        with open(private_key_filepath, "r") as file:
            ssh_private_key = file.read()
    except FileNotFoundError:
        raise Exception(
            "Failed to create default credentials:"
            f" SSH private key not found at {private_key_filepath}"
        )
    credentials = Credentials(
        connector="openwisp_controller.connection.connectors.ssh.Ssh",
        name="OpenWISP Default",
        auto_add=True,
        params={"username": "root", "key": ssh_private_key},
    )
    credentials.full_clean()
    credentials.save()
    return credentials


def create_ssh_key_template():
    if Template.objects.filter(
        default=True, config__contains="/etc/dropbear/authorized_keys"
    ).exists():
        return Template.objects.filter(
            default=True, config__contains="/etc/dropbear/authorized_keys"
        ).first()
    public_key_filepath = os.environ["SSH_PUBLIC_KEY_PATH"]
    try:
        with open(public_key_filepath, "r") as file:
            ssh_public_key = file.read()
    except FileNotFoundError:
        raise Exception(
            "Failed to default SSH Template:"
            f" SSH public key not found at {public_key_filepath}"
        )
    template = Template(
        name="SSH Keys",
        default=True,
        backend="netjsonconfig.OpenWrt",
        config={
            "files": [
                {
                    "path": "/etc/dropbear/authorized_keys",
                    "mode": "0644",
                    "contents": ssh_public_key,
                },
            ]
        },
    )
    template.full_clean()
    template.save()
    return template


def update_default_site():
    """Update default site with DASHBOARD_DOMAIN."""
    if "django.contrib.sites" in settings.INSTALLED_APPS:
        from django.contrib.sites.models import Site

        site = Site.objects.first()
        dashboard_domain = os.environ.get("DASHBOARD_DOMAIN", "")
        if site and "example.com" in [site.name, site.domain] and dashboard_domain:
            site.name = dashboard_domain
            site.domain = dashboard_domain
            site.save()


def create_default_topology(vpn):
    """Creates Topology object for the default VPN."""
    if vpn.backend == "openwisp_controller.vpn_backends.OpenVpn":
        parser = "netdiff.OpenvpnParser"
    topology_label = f"{vpn.name} ({vpn.get_backend_display()})"
    if Topology.objects.exists():
        try:
            topology = Topology.objects.get(label=topology_label)
        except Topology.DoesNotExist:
            topology = Topology.objects.first()
        if redis_client.get("default_openvpn_topology_uuid"):
            # The Topology UUID and key has already been set in Redis.
            return topology
    else:
        topology = Topology(
            label=topology_label,
            parser=parser,
            strategy="receive",
        )
        topology.full_clean()
        topology.save()
    redis_client.set("default_openvpn_topology_uuid", str(topology.id), ex=None)
    redis_client.set("default_openvpn_topology_key", str(topology.key), ex=None)
    return topology


if __name__ == "__main__":
    from django.contrib.auth import get_user_model
    from swapper import load_model

    Ca = load_model("pki", "Ca")
    Cert = load_model("pki", "Cert")
    Template = load_model("config", "Template")
    Vpn = load_model("config", "Vpn")
    Credentials = load_model("connection", "Credentials")
    User = get_user_model()
    # We don't write with Django's cache mechanism because
    # it serializes the data and augment's it with Django specific
    # metadata. This creates unnecessary overhead when we are
    # reading data using redis-cli.
    redis_client = redis.Redis.from_url(settings.CACHES["default"]["LOCATION"])

    create_admin()
    update_default_site()
    # Steps for creating new vpn client template with all the
    # required objects (CA, Certificate, VPN Server).
    is_vpn_enabled = os.environ.get("VPN_DOMAIN", "") != ""
    if is_vpn_enabled:
        default_ca = create_default_ca()
        default_cert = create_default_cert(default_ca)
        default_vpn = create_default_vpn(
            default_ca,
            default_cert,
        )
        create_default_vpn_template(default_vpn)

    create_default_credentials()
    create_ssh_key_template()

    if is_vpn_enabled and env_bool(os.environ.get("USE_OPENWISP_TOPOLOGY")):
        Topology = load_model("topology", "Topology")
        create_default_topology(default_vpn)

    try:
        # Force RDB save to avoid data loss
        redis_client.save()
    except redis.exceptions.ResponseError:
        # Redis server may not support RDB save command,
        # so we ignore the error.
        pass
