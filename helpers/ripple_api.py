import requests, json


def user(id=None, name=None):
    try:
        request = requests.get("https://ripple.moe/api/v1/users/full", params={"name": name, "id": id})
    except requests.exceptions.RequestException as e:
        return
    return json.loads(request.text)


def isonline(id=None):
    try:
        request = requests.get("https://c.ripple.moe/api/v1/isOnline", params={"id": id})
        return json.loads(request.text)
    except requests.exceptions.RequestException:
        return


def bid(id):
    return requests.get("https://storage.ripple.moe/api/b/%s" % id).json()


def sid(id):
    return requests.get("https://storage.ripple.moe/api/s/%s" % id).json()


def md5(id):
    try:
        request = requests.get("https://ripple.moe/api/v1/get_beatmaps", params={"h": id})
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
