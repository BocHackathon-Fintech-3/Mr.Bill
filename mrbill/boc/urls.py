from django.urls import path, re_path
from .views import authentication_success, authorize_boc_account, authorize_boc_account_empty

urlpatterns = [
    path('authorize_boc_account', authorize_boc_account_empty, name='boc_auth_account_empty'),
    path('<uuid:client_id>/authorize_boc_account', authorize_boc_account, name='boc_auth_account'),
    path('<uuid:client_id>/subscriptions/<str:subscription_id>/authentication_success/', authentication_success, name='boc_accounts_selected'),
]
