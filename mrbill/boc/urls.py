
from django.urls import path
from .views import authentication_success
urlpatterns = [
    path('authentication_success/', authentication_success),
]
