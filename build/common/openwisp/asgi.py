import os
from channels.asgi import get_channel_layer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "openwisp.settings")

channel_layer = get_channel_layer()

# Channels: 2
# """
# ASGI entrypoint. Configures Django and then runs the application
# defined in the ASGI_APPLICATION setting.
# """

# import os
# import django
# from channels.routing import get_default_application

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "openwisp.settings")
# django.setup()
# application = get_default_application()
