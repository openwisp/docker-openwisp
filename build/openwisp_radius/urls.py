from django.conf.urls import include, url

urlpatterns = [
    url(r'^', include('openwisp_radius.urls', namespace='freeradius')),
]
