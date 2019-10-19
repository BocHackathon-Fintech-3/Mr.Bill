from django.urls import path
from .views import webhook, client_config
urlpatterns = [
    path('webhook/', webhook),
    path('configuration/<uuid:client_id>/start/', client_config, name='fb_configuration_start')
]
