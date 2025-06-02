# Initial data for running the tests

from openwisp_controller.config.models import Config, Device
from openwisp_radius.models import (
    OrganizationRadiusSettings,
    RadiusGroup,
    RadiusUserGroup,
)
from openwisp_users.models import Organization, OrganizationUser, User


def get_organization():
    """Fetch default organization."""
    return Organization.objects.get(slug="default")


def get_admin():
    """Fetch superuser: admin."""
    return User.objects.get(username="admin")


def get_default_radius_group():
    """Fetch "default-users" radius group."""
    return RadiusGroup.objects.get(name="default-users")


def set_default_radius_token(radiusOrg):
    """Set "defaultapitoken" to the given organization."""
    radiusConf = OrganizationRadiusSettings.objects.filter(organization=radiusOrg)
    if not radiusConf.exists():
        radiusConf = OrganizationRadiusSettings()
        radiusConf.organization = radiusOrg
        radiusConf.token = "defaultapitoken"
        radiusConf.save()
    return radiusConf


def create_default_organizationUser(defOrg, admin):
    """Add superuser "admin" OrganizationUser of "default" organization."""
    orgUser = OrganizationUser.objects.filter(organization=defOrg)
    if not orgUser.exists():
        orgUser = OrganizationUser()
        orgUser.organization = defOrg
        orgUser.user = admin
        orgUser.full_clean()
        orgUser.save()
    return orgUser


def create_default_radiusUser(admin, radGroup):
    """Add superuser "admin" to "default-users" radius user group."""
    radiusUser = RadiusUserGroup.objects.filter(username="admin")
    if not radiusUser.exists():
        radiusUser = RadiusUserGroup()
        radiusUser.group = radGroup
        radiusUser.user = admin
        radiusUser.full_clean()
        radiusUser.save()
    return radiusUser


def create_device(organization):
    if Device.objects.filter(name="test-device").exists():
        return Device.objects.get(name="test-device")
    device = Device(
        name="test-device", mac_address="11:22:33:44:55:66", organization=organization
    )
    device.full_clean()
    device.save()
    config = Config(device=device, backend="netjsonconfig.OpenWrt")
    config.full_clean()
    config.save()
    return device


def setup():
    defOrg = get_organization()
    admin = get_admin()
    radGroup = get_default_radius_group()
    create_default_organizationUser(defOrg, admin)
    create_default_radiusUser(admin, radGroup)
    set_default_radius_token(defOrg)
    create_device(defOrg)


if __name__ == "__main__":
    setup()
