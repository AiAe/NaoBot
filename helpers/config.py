import json

def ripple():
    with open("./ripple.json", "r") as f:
        ripple = json.load(f)

    return ripple


def twitch():
    with open("./twitch.json", "r") as f:
        twitch = json.load(f)

    return twitch
