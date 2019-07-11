"""
Creates the admin user when openwisp2 is installed
"""

import json
import os
import django

from django.conf import settings
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'openwisp.settings')
django.setup()

from openwisp_radius.models import OrganizationRadiusSettings
from openwisp_users.models import Organization
from openwisp_controller.config.models import Vpn, Template
from openwisp_controller.pki.models import Ca, Cert

User = get_user_model()

# Default Superuser
User.objects.filter(is_superuser=True).exists() or \
    User.objects.create_superuser("admin", "admin@example.com", "admin")

# Default management VPN
defaultOrg = Organization.objects.get(slug=os.environ['DEFAULT_ORG'])

if not Ca.objects.filter(name='default').exists():
    defaultCa = Ca()
    defaultCa.organization = defaultOrg
    defaultCa.name = 'default'
    defaultCa.notes = 'This CA was created during the setup, it is used for the default management VPN.'
    defaultCa.full_clean()
    defaultCa.save()
defaultCa = Ca.objects.get(name='default')

if not Cert.objects.filter(name='default').exists():
    defaultCert = Cert()
    defaultCert.ca = defaultCa
    defaultCert.organization = defaultOrg
    defaultCert.name = 'default'
    defaultCert.notes = 'This certificate was created during the setup, it is used for the default management VPN.'
    defaultCert.full_clean()
    defaultCert.save()
defaultCert = Cert.objects.get(name='default')

if not Vpn.objects.filter(name='default').exists():
    defaultVpn = Vpn()
    defaultVpn.organization = defaultOrg
    defaultVpn.ca = defaultCa
    defaultVpn.cert = defaultCert
    defaultVpn.name = 'default'
    defaultVpn.notes = 'This is the default management VPN created during setup, you may modify these settings and they will soon reflect in your OpenVPN instance.'
    defaultVpn.host = 'openvpn'
    defaultVpn.backend = 'django_netjsonconfig.vpn_backends.OpenVpn'
    with open('openvpn.json', 'r') as json_file:
        json_data = json.load(json_file)
    defaultVpn.config = json_data
    defaultVpn.full_clean()
    defaultVpn.save()
defaultVpn = Vpn.objects.get(name='default')

if not Template.objects.filter(name='management-vpn').exists():
    defaultTp = Template()
    defaultTp.organization = defaultOrg
    defaultTp.auto_cert = True
    defaultTp.name = 'management-vpn'
    defaultTp.type = 'vpn'
    defaultTp.tags = 'Management, VPN'
    defaultTp.backend = 'netjsonconfig.OpenWrt'
    defaultTp.vpn = defaultVpn
    defaultTp.full_clean()
    defaultTp.save()
