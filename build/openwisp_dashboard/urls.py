from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import reverse_lazy
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from openwisp.utils import openwisp_topology_urls, openwisp_controller_urls

redirect_view = RedirectView.as_view(url=reverse_lazy('admin:index'))

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^accounts/', include('openwisp_users.accounts.urls')),
    url(r'^$', redirect_view, name='index'),
    url(r'^', include('openwisp_radius.urls', namespace='freeradius')),
]

urlpatterns += openwisp_controller_urls()
urlpatterns += openwisp_topology_urls()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()
