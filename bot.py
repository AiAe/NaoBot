import json
import asyncio
import bottom
import requests
import re
import websockets
from helpers import config, mysql, ripple_api
from irc import Dispatcher, connector, cooldown

bot_ripple = bottom.Client(host=config.ripple()["irc_ip"], port=config.ripple()["irc_port"], ssl=False)
bot_twitch = bottom.Client(host=config.twitch()["irc_ip"], port=config.twitch()["irc_port"], ssl=False)


async def RippleWebsocket():
    await bot_ripple.wait("client_connect")

    async with websockets.connect('wss://api.ripple.moe/api/v1/ws') as websocket:

        await websocket.send(ripple_api.get_users())
        #await websocket.send('{ "type": "subscribe_scores", "data": [] }')

        while True:
            get = await websocket.recv()

            # bot_ripple.send("privmsg", target="Ban_Hammer", message=get)
            print(get)


class RippleBot(Dispatcher):

    @cooldown(20)
    def help(self, nick, message, channel):
        print('ha')

    def command_patterns(self):
        return (
            ('!help', self.help),
        )


class TwitchBot(Dispatcher):

    @cooldown(20)
    def beatmap_request(self, nick, message, channel):
        print('ha')

    def command_patterns(self):
        return (
            ('^http[s]?:\/\/osu\.ppy\.sh\/(b|s)\/[0-9]+', self.beatmap_request),
        )


ripple_dispatcher = RippleBot(bot_ripple)
twitch_dispatcher = TwitchBot(bot_twitch)

connector(bot_ripple, ripple_dispatcher, config.ripple()["irc_username"], "", config.ripple()["irc_password"])
connector(bot_twitch, twitch_dispatcher, config.twitch()["irc_username"], "", config.twitch()["irc_password"])

bot_ripple.loop.create_task(RippleWebsocket())
bot_ripple.loop.create_task(bot_ripple.connect())
bot_ripple.loop.create_task(bot_twitch.connect())
bot_ripple.loop.run_forever()
