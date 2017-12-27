import requests


def get_users():
    try:
        request = requests.get("https://bot.aiae.ovh/api/users/")
        return request.text
    except requests.exceptions.RequestException:
        return
