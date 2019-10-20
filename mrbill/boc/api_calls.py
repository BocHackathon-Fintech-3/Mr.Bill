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
        payload['code'] = auth_code
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
        "app_name": "abc",
        "tppId": "singpaymentdata",
        "originUserId": "abc",
        "timestamp": "%s" % int(datetime.datetime.now().timestamp()),
        "journeyId": "abc",
    }
    res = requests.post(url, json=payload, headers=headers, params=params)
    res_json = res.json()
    print(res.text)
    return res_json


def patch_subscription(access_token, subscription_id, subscription_details):
    url = _get_url('/v1/subscriptions/%s' % subscription_id)
    params = {
        'client_id': settings.BOC_CLIENT_ID,
        'client_secret': settings.BOC_CLIENT_SECRET,
    }
    del subscription_details['subscriptionId']
    del subscription_details['status']
    payload = subscription_details
    headers = {
        'Authorization': "Bearer %s" % access_token,
        "content-type": "application/json",
        "tppId": "singpaymentdata",
        "originUserId": "abc",
        "timestamp": "%s" % int(datetime.datetime.now().timestamp()),
        "journeyId": "abc",
    }
    res = requests.patch(url, json=payload, headers=headers, params=params)
    print(res.text)
    res_json = res.json()
    return res_json


def get_accounts_boc_approval_url(access_token, subscription_id, redirect_uri):
    params = {
        "response_type": 'code',
        "redirect_uri": redirect_uri,
        "scope": "UserOAuth2Security",
        'client_id': settings.BOC_CLIENT_ID,
        "subscriptionid": subscription_id
    }
    url = _get_url('/oauth2/authorize?%s' % urllib.parse.urlencode(params))
    print(url)
    return url


def get_subscription_details(access_token, subscription_id):
    url = _get_url('/v1/subscriptions/%s' % subscription_id)
    params = {
        'client_id': settings.BOC_CLIENT_ID,
        'client_secret': settings.BOC_CLIENT_SECRET,
    }

    headers = {
        'Authorization': "Bearer %s" % access_token,
        "content-type": "application/json",
        "tppId": "singpaymentdata",
        "originUserId": "abc",
        "timestamp": "%s" % int(datetime.datetime.now().timestamp()),
        "journeyId": "abc",
    }
    res = requests.get(url, data='', headers=headers, params=params)
    print(res.text)
    res_json = res.json()
    return res_json


def get_accounts_balances(client):
    url = _get_url('/v1/accounts')

    params = {
        'client_id': settings.BOC_CLIENT_ID,
        'client_secret': settings.BOC_CLIENT_SECRET,
    }
    headers = {
        'Authorization': "Bearer %s" % client.active_access_token,
        "content-type": "application/json",
        "subscriptionid": client.active_subscription_id,
        "tppId": "singpaymentdata",
        "originUserId": "abc",
        "timestamp": "%s" % int(datetime.datetime.now().timestamp()),
        "journeyId": "abc",
    }

    response = requests.request("GET", url, headers=headers, params=params)

    print(response.text)
    '''Example response
      [
          {
            "bankId": "4150386227150848",
            "accountId": "4903671566156053",
            "accountAlias": "5018120785443735",
            "accountType": "3528496718001131",
            "accountName": "4540952894405290",
            "IBAN": "nobd",
            "currency": "TVD",
            "infoTimeStamp": "203703122",
            "interestRate": 39.08073206,
            "maturityDate": "2/24/2056",
            "lastPaymentDate": "Sims",
            "nextPaymentDate": "1/13/2099",
            "remainingInstallments": 84.0465412,
            "balances": [
              {
                "amount": 78.67365883,
                "balanceType": "hovarihe"
              }
            ]
          }
        ]
      '''
    res_json = response.json()
    balances = [{"accountId": x['accountId'], "balance": x['balances'][0]['amount']} for x in res_json]
    return balances


def make_payment_to_account(bill, client_account_id):
    url = _get_url('/v1/accounts')
    client = bill.client
    vendor = bill.vendor

    params = {
        'client_id': settings.BOC_CLIENT_ID,
        'client_secret': settings.BOC_CLIENT_SECRET,
    }
    headers = {
        'Authorization': "Bearer %s" % client.active_access_token,
        "content-type": "application/json",
        "subscriptionid": client.active_subscription_id,
        "tppId": "singpaymentdata",
        "originUserId": "abc",
        "timestamp": "%s" % int(datetime.datetime.now().timestamp()),
        "journeyId": "abc",
    }
    payload = {"debtor":
                   {"bankId": "4716483577905152",
                    "accountId": client_account_id},
               "creditor":
                   {"bankId": "4716483577905152",
                    "accountId": vendor.bank_account_no,
                    "name": vendor.name,
                    "address": "Missing"},
               "transactionAmount":
                   {"amount": bill.amount,
                    "currency": "EUR",
                    },
               "endToEndId": "unknown",
               "paymentDetails": "unknown",
               "terminalId": "unknown",
               "branch": "unknown",
               "executionDate": datetime.datetime.now().strftime("%d/%M/%YYY"),
               "valueDate": datetime.datetime.now().strftime("%d/%M/%YYY"),
               }

    response = requests.post(url, json=payload, headers=headers, params=params)
    res_json = response.json()
    return res_json
