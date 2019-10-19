from django.conf import settings
import requests
import datetime
import urllib


def _get_url(suburl):
    return "%s%s" % (settings.BOC_API_URL, suburl)


def get_access_token(auth_code=None):
    # TODO using auth_code

    url = _get_url("/oauth2/token")

    payload = {
        'client_id': settings.BOC_CLIENT_ID,
        'client_secret': settings.BOC_CLIENT_SECRET,

    }
    if auth_code:
        payload['grant_type'] = 'authorization_code'
        payload['scope'] = 'UserOAuth2Security'
        payload['code'] = 'auth_code'
    else:
        payload['grant_type'] = 'client_credentials'
        payload['scope'] = 'TPPOAuth2Security'

    headers = {
        'content-type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache",
    }

    response = requests.request("POST", url, data=payload, headers=headers)

    print(response.text)
    return response.json()['access_token']


def get_subscription_id(access_token):
    url = _get_url('/v1/subscriptions')
    params = {
        'client_id': settings.BOC_CLIENT_ID,
        'client_secret': settings.BOC_CLIENT_SECRET,
    }
    payload = {
        "accounts": {
            "transactionHistory": True,
            "balance": True,
            "details": True,
            "checkFundsAvailability": True
        },
        "payments": {
            "limit": 99999999,
            "currency": "EUR",
            "amount": 999999999
        }
    }
    headers = {
        'content-type': "application/json",
        'Authorization': "Bearer %s" % access_token,
        "Content-Type": "application/json",
        "APIm-Debug-Trans-Id": "true",
        "app_name": "MrBill",
        "tppid": "singpaymentdata",
        "originUserId": "mrbill",
        "timeStamp": "%s" % datetime.datetime.now().isoformat(),
        "journeyId": "abc",
    }
    res = requests.post(url, json=payload, headers=headers, params=params)
    res_json = res.json()
    print(res.text)
    return res_json




def patch_subscription(access_token, subscription_id):
    url = _get_url('/v1/subscriptions/%s' % subscription_id)
    params = {
        'client_id': settings.BOC_CLIENT_ID,
        'client_secret': settings.BOC_CLIENT_SECRET,
    }
    payload = {
        "accounts": {
            "transactionHistory": True,
            "balance": True,
            "details": True,
            "checkFundsAvailability": True
        },
        "payments": {
            "limit": 99999999,
            "currency": "EUR",
            "amount": 999999999
        }
    }
    headers = {
        'content-type': "application/json",
        'Authorization': "Bearer %s" % access_token,
        "Content-Type": "application/json",
        "APIm-Debug-Trans-Id": "true",
        "app_name": "MrBill",
        "tppid": "singpaymentdata",
        "originUserId": "mrbill",
        "timeStamp": "%s" % datetime.datetime.now().isoformat(),
        "journeyId": "abc",
    }
    res = requests.patch(url, json=payload, headers=headers, params=params)
    res_json = res.json()
    print(res.text)
    return res_json


def get_accounts_boc_approval_url(access_token, subscription_id, redirect_uri):

    params = {
        "response_type":'code',
        "redirect_uri": redirect_uri,
        "scope": "UserOAuth2Security",
        'client_id': settings.BOC_CLIENT_ID,
        "subscriptionId": subscription_id
    }
    url = _get_url('/oauth2/authorize?%s' % urllib.parse.urlencode(params))
    print(url)
    return url
