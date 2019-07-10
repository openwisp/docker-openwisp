# Initial data for running the tests

from django.conf import settings
from django.contrib.auth import get_user_model

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'openwisp.settings')
django.setup()
User = get_user_model()


def get_organization():
    '''
    Fetch default organization
    '''
    return Organization.objects.get(slug='default')


def get_admin():
    '''
    Fetch superuser: admin
    '''
    return User.objects.get(username='admin')


def get_default_radius_group():
    '''
    Fetch "default-users" radius group.
    '''
    return RadiusGroup.objects.get(name='default-users')


def set_default_radius_token(radiusOrg):
    '''
    Set "defaultapitoken" to the given organization.
    '''
    radiusConf = OrganizationRadiusSettings.objects \
                                           .filter(organization=radiusOrg)
    if not radiusConf.exists():
        radiusConf = OrganizationRadiusSettings()
        radiusConf.organization = radiusOrg
        radiusConf.token = 'defaultapitoken'
        radiusConf.save()
    return radiusConf


def create_default_organizationUser(defOrg, admin):
    '''
    Add superuser "admin" OrganizationUser of "default"
    organization.
    '''
    orgUser = OrganizationUser.objects.filter(organization=defOrg)
    if not orgUser.exists():
        orgUser = OrganizationUser()
        orgUser.organization = defOrg
        orgUser.user = admin
        orgUser.full_clean()
        orgUser.save()
    return orgUser


def create_default_radiusUser(admin, radGroup):
    '''
    Add superuser "admin" to "default-users" radius
    user group.
    '''
    radiusUser = RadiusUserGroup.objects.filter(username='admin')
    if not radiusUser.exists():
        radiusUser = RadiusUserGroup()
        radiusUser.group = radGroup
        radiusUser.user = admin
        radiusUser.full_clean()
        radiusUser.save()
    return radiusUser


if __name__ == "__main__":
    from openwisp_users.models import OrganizationUser, Organization
    from openwisp_radius.models import RadiusUserGroup, RadiusGroup, OrganizationRadiusSettings
    defOrg = get_organization()
    admin = get_admin()
    radGroup = get_default_radius_group()
    create_default_organizationUser(defOrg, admin)
    create_default_radiusUser(admin, radGroup)
    set_default_radius_token(defOrg)
