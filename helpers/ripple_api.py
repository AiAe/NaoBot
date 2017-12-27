import requests, json

def user(id=None, name=None):
    try:
        request = requests.get("https://ripple.moe/api/v1/users/full", params={"name" : name, "id" : id})
    except requests.exceptions.RequestException as e:
        return
    return json.loads(request.text)

def recent(id=None, limit=1):
    try:
        request = requests.get("https://ripple.moe/api/v1/users/scores/recent", params={"id" : id, "l" : limit})
        return json.loads(request.text)
    except requests.exceptions.RequestException:
        return

def isonline(id=None):
    try:
        request = requests.get("https://c.ripple.moe/api/v1/isOnline", params={"id": id})
        return json.loads(request.text)
    except requests.exceptions.RequestException:
        return

def bid(id):
    try:
        request = requests.get("https://storage.ripple.moe/api/b/%s" % id)
        return json.loads(request.text)
    except requests.exceptions.RequestException:
        return

def sid(id):
    try:
        request = requests.get("https://woostorage.ripple.moe/api/s/%s" % id)
        return json.loads(request.text)
    except requests.exceptions.RequestException:
        return

def md5(id):
    try:
        request = requests.get("https://ripple.moe/api/v1/get_beatmaps", params={"h" : id})
        return json.loads(request.text)
    except requests.exceptions.RequestException as e:
        return

def webdata():
    try:
        request = requests.get("https://bot.aiae.ovh/api/users/")
        return request.text
    except requests.exceptions.RequestException:
        return

def leaderboard(beatmapid="BG", mode=0):
    try:
        request = requests.get("https://ripple.moe/api/v1/scores", params={"b" : beatmapid, "mode": mode})
        return json.loads(request.text)
    except requests.exceptions.RequestException as e:
        return

def findLastDiff(js):
    i = 0
    arr = []
    arr2 = []
    for n in js["ChildrenBeatmaps"]:
        arr.append(js["ChildrenBeatmaps"][i]["DifficultyRating"])
        i = i + 1
        order = arr.index(max(arr))
        max_star = max(arr)
        id = js["ChildrenBeatmaps"][order]["BeatmapID"]
    arr2.append(order)
    arr2.append(id)
    return arr2