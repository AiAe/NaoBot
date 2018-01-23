import json
import os


def ripple():
    try:
        with open(os.getcwd() + "/ripple.json", "r") as f:
            cripple = json.load(f)
    except FileNotFoundError:
        with open("/home/ubuntu/NaoBot/ripple.json", "r") as f:
            cripple = json.load(f)

    return cripple


def twitch():
    try:
        with open(os.getcwd() + "/twitch.json", "r") as f:
            ctwitch = json.load(f)
    except FileNotFoundError:
        with open("/home/ubuntu/NaoBot/twitch.json", "r") as f:
            ctwitch = json.load(f)

    return ctwitch
