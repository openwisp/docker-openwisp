import os

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path, reverse_lazy
from django.views.generic import RedirectView
from openwisp.utils import env_bool, openwisp_controller_urls

index_redirect_view = RedirectView.as_view(url=reverse_lazy("admin:index"))

urlpatterns = [
    path("", index_redirect_view, name="index"),
    path("admin/", admin.site.urls),
    path("accounts/", include("openwisp_users.accounts.urls")),
]

urlpatterns += openwisp_controller_urls()

if env_bool(os.environ["USE_OPENWISP_MONITORING"]):
    urlpatterns += [
        path("", include("openwisp_monitoring.urls")),
    ]

if env_bool(os.environ["USE_OPENWISP_TOPOLOGY"]):
    from openwisp_network_topology.visualizer import urls as visualizer_urls

    urlpatterns += [path("topology/", include(visualizer_urls))]

if env_bool(os.environ["USE_OPENWISP_FIRMWARE"]):
    # When using S3_REVERSE_PROXY feature of django-private-storage,
    # the storage backend reverse the "serve_private_file" URL
    # pattern in order to proxy the file with the correct URL.
    from openwisp_firmware_upgrader.private_storage.urls import (
        urlpatterns as fw_private_storage_urls,
    )

    urlpatterns += [
        path(
            "",
            include((fw_private_storage_urls, "firmware"), namespace="firmware"),
        )
    ]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()
