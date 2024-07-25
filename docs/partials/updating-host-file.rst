.. important::

    A Docker OpenWISP installation responds only to the `fully qualified
    domain names (FQDN)
    <https://en.wikipedia.org/wiki/Fully_qualified_domain_name>`_ defined
    in the :ref:`configuration <docker_essential_env>`. If you are
    deploying locally (for testing), you need to update the ``/etc/hosts``
    file on your machine to resolve the configured domains to localhost.

    For example, the following command will update the ``/etc/hosts`` file
    to resolve the domains used in the default configurations:

    .. code-block:: bash

        echo "127.0.0.1 dashboard.openwisp.org api.openwisp.org openvpn.openwisp.org" | \
            sudo tee -a /etc/hosts
