import requests.auth
from scrt import *


def get_token():
    client_auth = requests.auth.HTTPBasicAuth(client_id, secret)
    post_data = {"grant_type": "password", "username": username, "password": password}
    headers = {"User-Agent": agent}
    response = requests.post("https://www.reddit.com/api/v1/access_token",
                             auth=client_auth, data=post_data, headers=headers)
    print(response.json())


def use_token():
    headers = {"Authorization": token['token_type'] + ' ' + token['access_token'], "User-Agent": agent}
    response = requests.get("https://oauth.reddit.com/api/v1/me", headers=headers)
    print(response.json())


if __name__ == '__main__':
    use_token()
