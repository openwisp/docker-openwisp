from django.urls import include, path
from openwisp_radius.api.urls import get_api_urls
from openwisp_radius.private_storage.views import rad_batch_csv_download_view

urlpatterns = [
    path('api/v1/', include((get_api_urls(), 'radius'), namespace='radius')),
    path(
        'radiusbatch/csv/<path:csvfile>',
        rad_batch_csv_download_view,
        name='serve_private_file',
    ),
]
