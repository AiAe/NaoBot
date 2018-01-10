import asyncio
import bottom
import json
import requests
import re
import websockets
from helpers import config, mysql, ripple_api, convertmods
from irc import Dispatcher, connector, cooldown

bot_ripple = bottom.Client(host=config.ripple()["irc_ip"], port=config.ripple()["irc_port"], ssl=False)
bot_twitch = bottom.Client(host=config.twitch()["irc_ip"], port=config.twitch()["irc_port"], ssl=False)


async def ripple_websocket():
    await bot_ripple.wait("client_connect")

    async with websockets.connect('wss://api.ripple.moe/api/v1/ws', timeout=1) as websocket:

        # await websocket.send(ripple_api.webdata())
        await websocket.send('{ "type": "subscribe_scores", "data": [] }')

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

                if message["data"]["user_id"] == 2185:

                    if message["data"]["pp"] > 0:

                        beatmap = ripple_api.md5(message["data"]["beatmap_md5"])

                        formatter = {
                            "b": beatmap[0]["beatmap_id"],
                            "song": "{} - {} [{}]".format(beatmap[0]["artist"], beatmap[0]["title"], beatmap[0]["version"]),
                            "mods": convertmods.ModsRev(message["data"]["mods"]),
                            "accuracy": message["data"]["accuracy"],
                            "rank": message["data"]["rank"],
                            "pp": message["data"]["pp"],
                            "stars": ""
                        }

                        username = ripple_api.user(message["data"]["user_id"])["username"].replace(" ", "_")

                        msg = "[https://osu.ppy.sh/b/{b} {song}]{mods} ({accuracy:.2f}%, {rank}) | {pp:.2f}pp".format(**formatter)

                        bot_ripple.send("privmsg", target=username, message=msg)


class RippleBot(Dispatcher):

    @cooldown(20)
    def help(self, nick, message, channel):
        self.respond(message="[https://bot.aiae.ovh/ To start using me click here to login]", nick=nick)

    def command_patterns(self):
        return (
            ('!help', self.help),
        )


class TwitchBot(Dispatcher):

    @cooldown(20)
    def beatmap_request(self, nick, message, channel):
        print('bm request')

    @cooldown(20)
    def np(self, nick, message, channel):
        print('np')

    def command_patterns(self):
        return (
            ('https?:\/\/osu\.ppy\.sh\/([bs])\/([0-9]+)(.*)', self.beatmap_request),
            ('!np', self.np),
        )


ripple_dispatcher = RippleBot(bot_ripple)
twitch_dispatcher = TwitchBot(bot_twitch)

connector(bot_ripple, ripple_dispatcher, config.ripple()["irc_username"], "", config.ripple()["irc_password"])
connector(bot_twitch, twitch_dispatcher, config.twitch()["irc_username"], "", config.twitch()["irc_password"])

bot_ripple.loop.create_task(ripple_websocket())
bot_ripple.loop.create_task(bot_ripple.connect())
bot_ripple.loop.create_task(bot_twitch.connect())
bot_ripple.loop.run_forever()
