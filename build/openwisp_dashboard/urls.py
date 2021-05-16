import os
from django.urls import include, path
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import reverse_lazy
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from openwisp.utils import openwisp_controller_urls, env_bool


index_redirect_view = RedirectView.as_view(url=reverse_lazy('admin:index'))

urlpatterns = [
    path('', index_redirect_view, name='index'),
    path('admin/', admin.site.urls),
    path('accounts/', include('openwisp_users.accounts.urls')),
]

urlpatterns += openwisp_controller_urls()

if env_bool(os.environ['USE_OPENWISP_TOPOLOGY']):
    from openwisp_network_topology.visualizer import urls as visualizer_urls

    urlpatterns += [path('topology/', include(visualizer_urls))]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()
