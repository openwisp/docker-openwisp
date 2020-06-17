from django.urls import include, path
from openwisp_radius.api.urls import get_api_urls

urlpatterns = [
    path('api/v1/', include((get_api_urls(), 'radius'), namespace='radius')),
]
