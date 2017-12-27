import json
import asyncio
import bottom
import requests
import re
from helpers import config, mysql
from irc import Dispatcher, connector, cooldown

bot_ripple = bottom.Client(host=config.ripple()["irc_ip"], port=config.ripple()["irc_port"], ssl=False)
bot_twitch = bottom.Client(host=config.twitch()["irc_ip"], port=config.twitch()["irc_port"], ssl=False)


class RippleBot(Dispatcher):

    @cooldown(20)
    def help(self):
        print('ha')

    def command_patterns(self):
        return (
            ('!help', self.help),
        )


class TwitchBot(Dispatcher):

    @cooldown(20)
    def beatmap_request(self):
        print('ha')

    def command_patterns(self):
        return (
            ('^http[s]?:\/\/osu\.ppy\.sh\/(b|s)\/[0-9]+', self.beatmap_request),
        )


ripple_dispatcher = RippleBot(bot_ripple)
twitch_dispatcher = TwitchBot(bot_twitch)

connector(bot_ripple, ripple_dispatcher, config.ripple()["irc_username"], "", config.ripple()["irc_password"])
connector(bot_twitch, twitch_dispatcher, config.twitch()["irc_username"], "", config.twitch()["irc_password"])

bot_ripple.loop.create_task(bot_ripple.connect())
bot_ripple.loop.create_task(bot_twitch.connect())
bot_ripple.loop.run_forever()