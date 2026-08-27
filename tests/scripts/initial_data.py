import os
from copy import deepcopy

import load_init_data
import redis
from django.conf import settings
from swapper import load_model

Ca = load_model("pki", "Ca")
Cert = load_model("pki", "Cert")
Template = load_model("config", "Template")
Topology = load_model("topology", "Topology")
Vpn = load_model("config", "Vpn")
client = redis.Redis.from_url(settings.CACHES["default"]["LOCATION"])
load_init_data.Ca = Ca
load_init_data.Cert = Cert
load_init_data.Template = Template
load_init_data.Topology = Topology
load_init_data.Vpn = Vpn
load_init_data.redis_client = client

keys = (
    "openwisp_default_vpn_uuid",
    "openwisp_default_vpn_template_uuid",
    "openwisp_default_ssh_template_uuid",
    "default_openvpn_topology_uuid",
    "default_openvpn_topology_key",
)
previous_values = {key: client.get(key) for key in keys}
default_vpn = Vpn.objects.get(pk=client.get("openwisp_default_vpn_uuid").decode())
default_template = Template.objects.get(vpn=default_vpn, default=True)
default_topology = Topology.objects.get(
    pk=client.get("default_openvpn_topology_uuid").decode()
)
ssh_template = Template.objects.get(name="SSH Keys", default=True)
marker = "initial-data-selector-decoy"
template_marker = "initial-data-selector-template"
ssh_template_marker = "initial-data-selector-ssh-template"
previous_vpn_name = default_vpn.name
previous_ssh_template_name = ssh_template.name
decoy_vpn = None
decoy_template = None
decoy_topology = None
previous_vpn_name_setting = os.environ.get("VPN_NAME")
previous_vpn_client_name_setting = os.environ.get("VPN_CLIENT_NAME")
try:
    Vpn.objects.filter(name=marker).delete()
    Template.objects.filter(name__in=(template_marker, ssh_template_marker)).delete()
    Topology.objects.filter(label=marker).delete()
    client.delete("openwisp_default_vpn_uuid")
    os.environ.pop("VPN_NAME", None)
    selected_vpn = load_init_data.create_default_vpn(None, None)
    assert (
        selected_vpn.pk == default_vpn.pk
    ), "VPN selector migration chose the wrong VPN"
    assert client.get("openwisp_default_vpn_uuid").decode() == str(default_vpn.pk)

    client.delete("default_openvpn_topology_uuid")
    selected_topology = load_init_data.create_default_topology(default_vpn)
    assert (
        selected_topology.pk == default_topology.pk
    ), "Topology selector migration chose the wrong topology"
    assert client.get("default_openvpn_topology_uuid").decode() == str(
        default_topology.pk
    )

    client.delete("openwisp_default_vpn_template_uuid")
    selected_template = load_init_data.create_default_vpn_template(default_vpn)
    assert (
        selected_template.pk == default_template.pk
    ), "VPN template selector migration chose the wrong template"
    assert client.get("openwisp_default_vpn_template_uuid").decode() == str(
        default_template.pk
    )

    client.delete("openwisp_default_ssh_template_uuid")
    selected_ssh_template = load_init_data.create_ssh_key_template()
    assert (
        selected_ssh_template.pk == ssh_template.pk
    ), "SSH template selector migration chose the wrong template"
    assert client.get("openwisp_default_ssh_template_uuid").decode() == str(
        ssh_template.pk
    )

    decoy_vpn = Vpn(
        name=marker,
        ca=default_vpn.ca,
        cert=default_vpn.cert,
        dh=default_vpn.dh,
        host=default_vpn.host,
        backend=default_vpn.backend,
        config=deepcopy(default_vpn.config),
    )
    decoy_vpn.full_clean()
    decoy_vpn.save()
    os.environ["VPN_NAME"] = marker
    selected_vpn = load_init_data.create_default_vpn(None, None)
    assert selected_vpn.pk == default_vpn.pk, "VPN name selected the wrong VPN"
    os.environ.pop("VPN_NAME")
    selected_vpn = load_init_data.create_default_vpn(None, None)
    assert selected_vpn.pk == default_vpn.pk, "Missing VPN name changed VPN selection"

    decoy_topology = Topology(
        label=f"{marker} ({decoy_vpn.get_backend_display()})",
        parser="netdiff.OpenvpnParser",
        strategy="receive",
    )
    decoy_topology.full_clean()
    decoy_topology.save()
    selected_topology = load_init_data.create_default_topology(decoy_vpn)
    assert (
        selected_topology.pk == default_topology.pk
    ), "Topology label selected the wrong topology"

    decoy_template = Template(
        name=template_marker,
        type=default_template.type,
        backend=default_template.backend,
        vpn=default_vpn,
        auto_cert=default_template.auto_cert,
        config=deepcopy(default_template.config),
    )
    decoy_template.full_clean()
    decoy_template.save()
    client.set("openwisp_default_vpn_template_uuid", str(default_template.pk))
    os.environ.pop("VPN_CLIENT_NAME", None)
    selected_template = load_init_data.create_default_vpn_template(default_vpn)
    assert (
        selected_template.pk == default_template.pk
    ), "VPN template selected the wrong template"

    ssh_template.name = ssh_template_marker
    ssh_template.full_clean()
    ssh_template.save()
    client.delete("openwisp_default_ssh_template_uuid")
    selected_ssh_template = load_init_data.create_ssh_key_template()
    assert (
        selected_ssh_template.pk == ssh_template.pk
    ), "SSH template selector migration created a duplicate"
    assert client.get("openwisp_default_ssh_template_uuid").decode() == str(
        ssh_template.pk
    )
    print("initial data selectors passed")
finally:
    if previous_vpn_name_setting is None:
        os.environ.pop("VPN_NAME", None)
    else:
        os.environ["VPN_NAME"] = previous_vpn_name_setting
    if previous_vpn_client_name_setting is None:
        os.environ.pop("VPN_CLIENT_NAME", None)
    else:
        os.environ["VPN_CLIENT_NAME"] = previous_vpn_client_name_setting
    if decoy_template:
        decoy_template.delete()
    Template.objects.exclude(pk=ssh_template.pk).filter(
        name="SSH Keys", default=True
    ).delete()
    ssh_template.name = previous_ssh_template_name
    ssh_template.full_clean()
    ssh_template.save()
    if decoy_topology:
        decoy_topology.delete()
    if decoy_vpn:
        decoy_vpn.delete()
    default_vpn.name = previous_vpn_name
    default_vpn.full_clean()
    default_vpn.save()
    for key, value in previous_values.items():
        if value is None:
            client.delete(key)
        else:
            client.set(key, value)
