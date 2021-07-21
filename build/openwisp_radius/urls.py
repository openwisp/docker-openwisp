from django.urls import include, path

urlpatterns = [
    path('', include('openwisp_radius.urls')),
]
