from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from . import api_calls
import pprint
from facebook.views import get_absolute_url


def authorize_boc_account_empty(request):
    print("Came here from BOC")
    auth_code = request.GET['code']
    access_token = request.session.get('access_token')
    access_token_2 = api_calls.get_access_token(auth_code)
    client_id = request.session.get('client_id')
    subscription_id = request.session.get('subscription_id')
    current_subscription_details = api_calls.get_subscription_details(access_token, subscription_id)
    #pprint.pprint(current_subscription_details)
    #subscription_response = api_calls.patch_subscription(access_token_2, subscription_id)
    #pprint.pprint(subscription_response)
    #subscription_id = subscription_response['subscriptionId']

    return HttpResponse("Boc")


def authentication_success(request, subscription_id):
    auth_code = request.GET['code']
    access_token = api_calls.get_access_token(auth_code)
    subscription_response = api_calls.patch_subscription(access_token, subscription_id)
    # pprint.pprint(subscription_response)
    subscription_id = subscription_response['subscriptionId']


def authorize_boc_account(request, client_id):
    access_token = api_calls.get_access_token()
    subscription_response = api_calls.get_subscription_id(access_token=access_token)
    # pprint.pprint(subscription_response)
    subscription_id = subscription_response['subscriptionId']

    # redirect_uri = reverse('boc_accounts_selected', kwargs={'client_id': client_id, 'subscription_id': subscription_id})

    redirect_uri = reverse('boc_auth_account_empty')
    request.session['client_id'] = str('client_id')
    request.session['subscription_id'] = subscription_id
    request.session['access_token'] = access_token

    url_to_redirect = api_calls.get_accounts_boc_approval_url(
        subscription_id=subscription_id,
        redirect_uri=get_absolute_url(redirect_uri),
        access_token=access_token,
    )
    return redirect(url_to_redirect)
