import asyncio
import bottom
import json
import re
import websockets
from helpers import config, ripple_api, convertmods, naoapi, generate
from irc import Dispatcher, connector, cooldown

bot_ripple = bottom.Client(host=config.ripple()["irc_ip"], port=config.ripple()["irc_port"], ssl=False)
bot_twitch = bottom.Client(host=config.twitch()["irc_ip"], port=config.twitch()["irc_port"], ssl=False)


def load_memes():
    arr = []
    players = naoapi.get_list()["data"]
    for player in players:
        arr.append(player["user_id"])
    return arr


async def ripple_websocket():
    await bot_ripple.wait("client_connect")

    async with websockets.connect("wss://api.ripple.moe/api/v1/ws", timeout=1) as websocket:

        await websocket.send('{"type": "subscribe_scores", "data": []}')

        while True:
            try:
                string_message = await asyncio.wait_for(websocket.recv(), timeout=10)
            except asyncio.TimeoutError:
                try:
                    await asyncio.wait_for(websocket.ping(), timeout=10)
                    continue
                except asyncio.TimeoutError:
                    return
            except websockets.exceptions.ConnectionClosed:
                return

            message = json.loads(string_message)

            if message["type"] == "new_score":
                p = load_memes()
                if message["data"]["user_id"] in p:
                    print('player in list')
                    if message["data"]["pp"] > 0:
                        beatmap = ripple_api.md5(message["data"]["beatmap_md5"])
                        play_mode = message["data"]["play_mode"]

                        if play_mode == 1:
                            mode = " <taiko> "
                        elif play_mode == 2:
                            mode = " <ctb> "
                        elif play_mode == 3:
                            mode = " <mania> "
                        else:
                            mode = ""

                        formatter = {
                            "b": beatmap[0]["beatmap_id"],
                            "song": "{} - {} [{}]".format(beatmap[0]["artist"], beatmap[0]["title"],
                                                          beatmap[0]["version"]),
                            "mods": convertmods.ModsRev(message["data"]["mods"]),
                            "accuracy": message["data"]["accuracy"],
                            "rank": message["data"]["rank"],
                            "pp": message["data"]["pp"],
                            "stars": "",
                            "mode": mode
                        }

                        username = ripple_api.user(message["data"]["user_id"])["username"].replace(" ", "_")

                        msg = "[https://osu.ppy.sh/b/{b} {song}]{mods}{mode}({accuracy:.2f}%, {rank}) | {pp:.2f}pp".format(
                            **formatter)

                        msg_twitch = "{song}{mods}{mode}({accuracy:.2f}%, {rank}) | {pp:.2f}pp".format(
                            **formatter)

                        try:
                            bot_ripple.send("privmsg", target=username, message=msg)
                            # bot_twitch.send("privmsg", target="#ayyayye", message=msg_twitch)
                        except:
                            print("Something went wrong with sending message.")


async def TwitchJoin():
    await bot_twitch.wait("client_connect")

    twitch_list = ["ayyayye"]

    '''
    Add to list joined channels from database so it can skip them...
    '''

    for channel in twitch_list:
        bot_twitch.send("JOIN", channel=("#" + channel))

    await asyncio.sleep(30, loop=bot_twitch.loop)


class RippleBot(Dispatcher):
    @cooldown(20)
    def help(self, nick, message, channel):
        self.respond(message="To start using me write !signup", nick=nick)

    @cooldown(60)
    def signup(self, nick, message, channel):
        user = ripple_api.user(name=nick)
        code = generate.code(16)
        insert_user = naoapi.insert_user(user["id"], code)

        if insert_user["code"] == "1":
            self.respond(message="You logged in successfully!", nick=nick)
            self.respond(message="To check list with commands write !commands", nick=nick)
        else:
            self.respond(message="You have account, or something went wrong!", nick=nick)

    @cooldown(20)
    def signup_twitch(self, nick, message, channel):
        user = ripple_api.user(name=nick)
        get_user = naoapi.get_user(user["id"])
        if get_user["code"] == "1":
            twitch_client = config.twitch()["twitch_client"]
            twitch_redirect = config.twitch()["twitch_redirect"]
            twitch_url = "https://api.twitch.tv/kraken/oauth2/authorize?" \
                         "response_type=code&client_id={}&redirect_uri={}" \
                         "&state={}".format(twitch_client, twitch_redirect,
                                            get_user["token"])
            self.respond(message="[{} Click here to connect to Twitch]".format(twitch_url), nick=nick)

    @cooldown(20)
    def commands(self, nick, message, channel):
        self.respond(message="For full list read [https://ripple.moe/u/9973 NaoBot] user page!", nick=nick)

    @cooldown(5)
    def settings(self, nick, message, channel):
        clean_message = message.split("!settings")[1]
        update = re.search("([A-Za-z_]+) ([A-Za-z0-9_.]+)", clean_message)
        user = ripple_api.user(name=nick)
        naoapi.update_settings(user["id"], update.group(1), update.group(2))

        self.respond(message="{} is changed to {}".format(update.group(1), update.group(2)), nick=nick)

    def shutdown(self, nick, message, channel):
        user = ripple_api.user(name=nick)
        get_user_full = naoapi.get_user_full(user["id"])

        if get_user_full["group"] == "Admin":
            self.respond(message="Sayonara", nick=nick)
            exit()

    def command_patterns(self):
        return (
            ("!help", self.help),
            ("!signup", self.signup),
            ("!commands", self.commands),
            ("!twitch", self.signup_twitch),
            ("!settings ([A-Za-z_]+) ([A-Za-z0-9.]+)", self.settings),
            ("!shutdown", self.shutdown),
        )


class TwitchBot(Dispatcher):
    @cooldown(20)
    def beatmap_request(self, nick, message, channel):
        username = nick.split(".")[0]
        try:
            groups = re.match("https?:\/\/osu\.ppy\.sh\/([bs])\/([0-9]+)(.*)", message).groups()
        except:
            groups = re.match("https?:\/\/ripple\.moe\/([bs])\/([0-9]+)(.*)", message).groups()

        idtype, bid, modsg = groups
        find_mods = []
        if modsg:
            find_mods = re.findall("(HR|DT|NC|FL|HD|EZ|HT)", modsg.upper())

        if idtype == "s":
            mapinfo = ripple_api.sid(bid)
        else:
            b_map = ripple_api.bid(bid)
            if b_map:
                mapinfo = ripple_api.sid(b_map["ParentSetID"])
            else:
                print('Map not found return link only to player...')
                msg = "{}: [https://osu.ppy.sh/{}/{}/ Requested map]".format(username, idtype, bid)
                bot_ripple.send("privmsg", target="Ban_Hammer", message=msg)
                return

        if idtype == "s":
            findHardestDifficulty = ripple_api.findLastDiff(mapinfo)
            beatMapSetId = mapinfo["SetID"]
            #mode = mapinfo["ChildrenBeatmaps"][findHardestDifficulty[0]]["Mode"]
            version = mapinfo["ChildrenBeatmaps"][findHardestDifficulty[0]]["DiffName"]
            stars = mapinfo["ChildrenBeatmaps"][findHardestDifficulty[0]]["DifficultyRating"]
            bpm = mapinfo["ChildrenBeatmaps"][findHardestDifficulty[0]]["BPM"]
        else:
            beatMapSetId = b_map["ParentSetID"]
            #mode = b_map["Mode"]
            version = b_map["DiffName"]
            stars = b_map["DifficultyRating"]
            bpm = b_map["BPM"]

        artist = mapinfo["Artist"]
        title = mapinfo["Title"]

        formatter = {
            "sender": username,
            "beatmapsetid": beatMapSetId,
            "artist": artist,
            "title": title,
            "bpm": bpm,
            "version": version,
            "stars": stars,
            "all_mods": ''.join(find_mods)
        }

        twitch = channel.split("#")[1]
        bot_ripple.send("privmsg", target="Ban_Hammer",
                        message="{sender}: [osu://dl/{beatmapsetid} {artist} - {title} [{version}]] {all_mods} {bpm}BPM {stars:.2f}★".format(
                            **formatter))

    @cooldown(20)
    def np(self, nick, message, channel):
        twitch = channel.split("#")[1]
        get_np = naoapi.get_tracking(twitch=twitch)
        current_map = get_np["nowplaying"]
        if current_map:
            msg = "Current map {}".format(get_np["nowplaying"])
            bot_twitch.send("privmsg", target=channel, message=msg)

    def command_patterns(self):
        return (
            ("https?:\/\/osu\.ppy\.sh\/([bs])\/([0-9]+)(.*)", self.beatmap_request),
            ("https?:\/\/ripple\.moe\/([bs])\/([0-9]+)(.*)", self.beatmap_request),
            ("!np|np", self.np),
        )


ripple_dispatcher = RippleBot(bot_ripple)
twitch_dispatcher = TwitchBot(bot_twitch)

connector(bot_ripple, ripple_dispatcher, config.ripple()["irc_username"], "", config.ripple()["irc_password"])
connector(bot_twitch, twitch_dispatcher, config.twitch()["irc_username"], "", config.twitch()["irc_password"])

bot_ripple.loop.create_task(ripple_websocket())
bot_ripple.loop.create_task(TwitchJoin())
bot_ripple.loop.create_task(bot_ripple.connect())
bot_ripple.loop.create_task(bot_twitch.connect())
bot_ripple.loop.run_forever()
