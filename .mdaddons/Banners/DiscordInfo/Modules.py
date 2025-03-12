import discord
import asyncio
import traceback
import os

from mcdis_rcon.classes import McDisClient
from discord.ext import commands
from datetime import datetime
from typing import Union
import pandas as pd


tickets_log = f'{os.path.dirname(__file__)}/TicketSystem/TicketsLog.csv'
form_log = f'{os.path.dirname(__file__)}/Form/FormsLog.csv'

config = {      
    'Thumbnail'         : 'https://i.postimg.cc/XqQx5rT5/logo.png',
    'Discord Invite'    : 'https://discord.gg/pXwV7BWd2P',
    'Link YouTube'      : 'https://www.youtube.com/channel/UCjjMAJirU2oWOrQPwGsDxYw',
    'Link Twitter'      : 'https://twitter.com/aeternum_smp',
    'Link Twitch'       : 'https://www.twitch.tv/aeternumsmp',
    'Link Overviewer'   : 'http://map.aeternumsmp.com:25589/',
    'Emoji Server'      : '<:aeternum:925134249865142303>',
    'Emoji Discord'     : '<:AeDiscord:1235343118484635739>',
    'Emoji YouTube'     : '<:AeYoutube:1235340762477236307>',
    'Emoji Twitch'      : '<:AeTwitch:1235342533299666944>',
    'Emoji Twitter'     : '<:AeTwitter:1235341007562870825>',
    'Emoji Overviewer'  : '🌐',
    'Foundation Date'   : '2021-05-12',
    'Channel ID'        : 1341217051158773871}
    
config_form = {      
    'Thumbnail'     : 'https://i.postimg.cc/XqQx5rT5/logo.png',
    'Emoji Yes'     : '<:PepeYes:887447915289776159>',
    'Emoji No'      : '<:PepeNo:887447914291560468>',
    'Channel ID'    : 1246511292576170054
    }

tickets_config = {      
    'Category ID'   : 892445913635778630,
    'Ticket Moderator ID' : 914530780523401267
    }