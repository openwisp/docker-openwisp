'''
Load initial data before starting the server.
- Create superuser `admin`.
- Create default CA
- Create default Cert
- Create default VPN
- Create default VPN Client Template
'''

import json
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'openwisp.settings')
django.setup()


def create_admin():
    """
    Creates superuser `admin` if it does not exist.
    """
    User.objects.filter(is_superuser=True).exists() or User.objects.create_superuser(
        "admin", "admin@example.com", "admin"
    )


def create_default_CA(x509NameCA):
    """
    Create default certificate authority
    """
    if not Ca.objects.filter(name=x509NameCA).exists():
        defaultCa = Ca()
        defaultCa.name = x509NameCA
        defaultCa.country_code = os.environ['X509_COUNTRY_CODE']
        defaultCa.state = os.environ['X509_STATE']
        defaultCa.city = os.environ['X509_CITY']
        defaultCa.organization_name = os.environ['X509_ORGANIZATION_NAME']
        defaultCa.organizational_unit_name = os.environ['X509_ORGANIZATION_UNIT_NAME']
        defaultCa.email = os.environ['X509_EMAIL']
        defaultCa.common_name = os.environ['X509_COMMON_NAME']
        defaultCa.notes = (
            'This CA was created during the setup, it is used for '
            'the default management VPN. Please do not rename it.'
        )
        defaultCa.full_clean()
        defaultCa.save()
        return defaultCa
    return Ca.objects.get(name=x509NameCA)


def create_default_cert(defaultCa, x509NameCert):
    """
    Create default certificate
    """
    if not Cert.objects.filter(name=x509NameCert).exists():
        defaultCert = Cert()
        defaultCert.ca = defaultCa
        defaultCert.name = x509NameCert
        defaultCert.country_code = os.environ['X509_COUNTRY_CODE']
        defaultCert.state = os.environ['X509_STATE']
        defaultCert.city = os.environ['X509_CITY']
        defaultCert.organization_name = os.environ['X509_ORGANIZATION_NAME']
        defaultCert.organizational_unit_name = os.environ['X509_ORGANIZATION_UNIT_NAME']
        defaultCert.email = os.environ['X509_EMAIL']
        defaultCert.common_name = os.environ['X509_COMMON_NAME']
        defaultCert.notes = (
            'This certificate was created during the setup. '
            'It is used for the default management VPN. '
            'Please do not rename it.'
        )
        defaultCert.full_clean()
        defaultCert.save()
        return defaultCert
    return Cert.objects.get(name=x509NameCert)


def create_default_vpn(vpnName, vpnDomain, defaultCa, defaultCert):
    """
    Create default vpn
    """
    if not Vpn.objects.filter(name=vpnName).exists():
        defaultVpn = Vpn()
        defaultVpn.ca = defaultCa
        defaultVpn.cert = defaultCert
        defaultVpn.name = vpnName
        defaultVpn.notes = (
            'This is the default management VPN created during setup, '
            'you may modify these settings and they will soon reflect '
            'in your OpenVPN Server instance.'
        )
        defaultVpn.host = vpnDomain
        defaultVpn.backend = 'openwisp_controller.vpn_backends.OpenVpn'
        with open('openvpn.json', 'r') as json_file:
            json_data = json.load(json_file)
        defaultVpn.config = json_data
        defaultVpn.full_clean()
        defaultVpn.save()
        return defaultVpn
    return Vpn.objects.get(name=vpnName)


def create_default_vpn_template(defaultVpnClient, defaultVpn):
    """
    Create default vpn client template
    """
    if not Template.objects.filter(name=defaultVpnClient).exists():
        defaultTp = Template()
        defaultTp.auto_cert = True
        defaultTp.name = defaultVpnClient
        defaultTp.type = 'vpn'
        defaultTp.tags = 'Management, VPN'
        defaultTp.backend = 'netjsonconfig.OpenWrt'
        defaultTp.vpn = defaultVpn
        defaultTp.default = True
        defaultTp.full_clean()
        defaultTp.save()


if __name__ == '__main__':
    from django.contrib.auth import get_user_model
    from swapper import load_model

    Ca = load_model('pki', 'Ca')
    Cert = load_model('pki', 'Cert')
    Template = load_model('config', 'Template')
    Vpn = load_model('config', 'Vpn')
    User = get_user_model()

    create_admin()
    # Steps for creating new vpn client template with all the
    # required objects (CA, Certificate, VPN Server).
    defaultCa = create_default_CA(os.environ['X509_NAME_CA'])
    defaultCert = create_default_cert(defaultCa, os.environ['X509_NAME_CERT'])
    defaultVpn = create_default_vpn(
        os.environ['VPN_NAME'],
        os.environ['VPN_DOMAIN'],
        defaultCa,
        defaultCert,
    )
    create_default_vpn_template(os.environ['VPN_CLIENT_NAME'], defaultVpn)
