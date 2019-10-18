from django.urls import path
from .views import incoming_mail_parse
urlpatterns = [
    path('incoming/', incoming_mail_parse),
]
