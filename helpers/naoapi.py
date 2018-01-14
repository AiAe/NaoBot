import requests
import json
import os

try:
    with open(os.getcwd() + "/api.json", "r") as f:
        config = json.load(f)
except FileNotFoundError:
    with open("/home/ubuntu/NaoBot/api.json", "r") as f:
        config = json.load(f)

url = config["url"]
token = config["token"]
'''
GET user data
'''


def get_user_full(user_id):
    return requests.get(url + "/full", params={"user_id": user_id, "token": token}).json()


def get_user(user_id):
    return requests.get(url + "/get_user", params={"user_id": user_id, "token": token}).json()


def get_settings(user_id):
    return requests.get(url + "/get_settings", params={"user_id": user_id, "token": token}).json()


def get_tracking(user_id):
    return requests.get(url + "/get_tracking", params={"user_id": user_id, "token": token}).json()


'''
POST user data
'''


def insert_user(user_id, code):
    return requests.post(url + "/insert/user", params={"user_id": user_id, "code": code, "token": token}).json()


def update_user(user_id, update, value):
    return requests.post(url + "/update/user",
                         params={"user_id": user_id, "update": update, "value": value, "token": token}).json()


def update_settings(user_id, update, value):
    return requests.post(url + "/update/settings",
                         params={"user_id": user_id, "update": update, "value": value, "token": token}).json()


def update_tracking(user_id, update, value):
    return requests.post(url + "/update/tracking",
                         params={"user_id": user_id, "update": update, "value": value, "token": token}).json()
