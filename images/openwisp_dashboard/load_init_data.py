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
import logging
import os

import django
import redis
import redis.exceptions
from openwisp.utils import env_bool

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "openwisp.settings")
django.setup()
from django.conf import settings  # noqa

DEFAULT_VPN_NAME = "default"
DEFAULT_VPN_CLIENT_NAME = "default-management-vpn"
DEFAULT_SSH_TEMPLATE_NAME = "SSH Keys"
DEFAULT_VPN_UUID_KEY = "openwisp_default_vpn_uuid"
DEFAULT_VPN_TEMPLATE_UUID_KEY = "openwisp_default_vpn_template_uuid"
DEFAULT_SSH_TEMPLATE_UUID_KEY = "openwisp_default_ssh_template_uuid"
DEFAULT_TOPOLOGY_UUID_KEY = "default_openvpn_topology_uuid"
logger = logging.getLogger(__name__)


def get_initial_name(variable, default):
    name = os.environ.get(variable)
    if name:
        logger.warning(
            "%s is deprecated and is used only for initial object creation.", variable
        )
        return name
    return default


def get_selected(model, key):
    identifier = redis_client.get(key)
    if identifier:
        if isinstance(identifier, bytes):
            identifier = identifier.decode()
        try:
            return model.objects.get(pk=identifier)
        except model.DoesNotExist:
            redis_client.delete(key)


def select_single(queryset, key, object_name):
    count = queryset.count()
    if count > 1:
        raise RuntimeError(
            f"Multiple {object_name} objects exist without a saved selector."
        )
    if count:
        instance = queryset.get()
        redis_client.set(key, str(instance.pk), ex=None)
        return instance


def set_default_vpn(vpn):
    redis_client.set(DEFAULT_VPN_UUID_KEY, str(vpn.id), ex=None)
    redis_client.set("openwisp_default_vpn_key", str(vpn.key), ex=None)
    redis_client.set("openwisp_default_vpn_ca_uuid", str(vpn.ca_id), ex=None)


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
            "This CA was created during setup and is used for the default "
            "management VPN."
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
            "This certificate was created during setup and is used for the "
            "default management VPN."
        ),
    )
    cert.full_clean()
    cert.save()
    return cert


def create_default_vpn(ca=None, cert=None):
    """Creates default vpn."""
    vpn = get_selected(Vpn, DEFAULT_VPN_UUID_KEY)
    if vpn:
        return vpn
    vpn_name = get_initial_name("VPN_NAME", DEFAULT_VPN_NAME)
    vpn = select_single(Vpn.objects.filter(name=vpn_name), DEFAULT_VPN_UUID_KEY, "VPN")
    if not vpn:
        vpn = select_single(Vpn.objects.all(), DEFAULT_VPN_UUID_KEY, "VPN")
    if vpn:
        set_default_vpn(vpn)
        return vpn
    ca = ca or create_default_ca()
    cert = cert or create_default_cert(ca)
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
    set_default_vpn(vpn)
    return vpn


def create_default_vpn_template(vpn):
    """Creates default vpn client template."""
    template = get_selected(Template, DEFAULT_VPN_TEMPLATE_UUID_KEY)
    if template:
        if template.vpn_id != vpn.id:
            raise RuntimeError(
                "The saved VPN template does not belong to the default VPN."
            )
        return template
    template = select_single(
        Template.objects.filter(vpn=vpn, type="vpn", default=True),
        DEFAULT_VPN_TEMPLATE_UUID_KEY,
        "VPN template",
    )
    if template:
        return template

    template = Template(
        auto_cert=True,
        name=get_initial_name("VPN_CLIENT_NAME", DEFAULT_VPN_CLIENT_NAME),
        type="vpn",
        tags="Management, VPN",
        backend="netjsonconfig.OpenWrt",
        vpn=vpn,
        default=True,
    )
    # The config field is auto-generated on full_clean()
    template.full_clean()
    if template.config.get("openvpn"):
        template.config["openvpn"][0]["log"] = "/var/log/tun0.log"
    # Verify that the config is still valid.
    template.full_clean()
    template.save()
    redis_client.set(DEFAULT_VPN_TEMPLATE_UUID_KEY, str(template.id), ex=None)
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
    template = get_selected(Template, DEFAULT_SSH_TEMPLATE_UUID_KEY)
    if template:
        return template
    template = select_single(
        Template.objects.filter(name=DEFAULT_SSH_TEMPLATE_NAME, default=True),
        DEFAULT_SSH_TEMPLATE_UUID_KEY,
        "SSH key template",
    )
    if template:
        return template
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
        name=DEFAULT_SSH_TEMPLATE_NAME,
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
    redis_client.set(DEFAULT_SSH_TEMPLATE_UUID_KEY, str(template.id), ex=None)
    return template


def update_default_site():
    """Update default site with DASHBOARD_DOMAIN."""
    if "django.contrib.sites" in settings.INSTALLED_APPS:
        from django.contrib.sites.models import Site

        try:
            site = Site.objects.get(pk=settings.SITE_ID)
        except Site.DoesNotExist:
            # Optionally log a message here if desired
            return
        dashboard_domain = os.environ.get("DASHBOARD_DOMAIN", "")
        if (
            site.name == "example.com" or site.domain == "example.com"
        ) and dashboard_domain:
            site.name = dashboard_domain
            site.domain = dashboard_domain
            site.full_clean()
            site.save()


def create_default_topology(vpn):
    """Creates Topology object for the default VPN."""
    topology = get_selected(Topology, DEFAULT_TOPOLOGY_UUID_KEY)
    if topology:
        return topology
    if vpn.backend == "openwisp_controller.vpn_backends.OpenVpn":
        parser = "netdiff.OpenvpnParser"
    topology_label = f"{vpn.name} ({vpn.get_backend_display()})"
    topology = select_single(
        Topology.objects.filter(label=topology_label),
        DEFAULT_TOPOLOGY_UUID_KEY,
        "topology",
    )
    if not topology:
        topology = select_single(
            Topology.objects.all(), DEFAULT_TOPOLOGY_UUID_KEY, "topology"
        )
    if not topology:
        topology = Topology(
            label=topology_label,
            parser=parser,
            strategy="receive",
        )
        topology.full_clean()
        topology.save()
    redis_client.set(DEFAULT_TOPOLOGY_UUID_KEY, str(topology.id), ex=None)
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
        default_vpn = create_default_vpn()
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
