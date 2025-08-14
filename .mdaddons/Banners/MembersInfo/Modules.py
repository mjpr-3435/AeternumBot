import pandas as pd
import numpy as np
import discord
import asyncio
import aiohttp
import traceback
import shutil
import json
import math
import os
import sys

from mcdis_rcon.utils import isAdmin, thread
from mcdis_rcon.classes import McDisClient, Server

from discord.app_commands import describe, choices, Choice
from discord.ext import commands
from datetime import datetime

tasks_log = os.path.join(os.path.dirname(__file__), 'TasksLog.csv')
whitelist_log = os.path.join(os.path.dirname(__file__), 'WhitelistLog.csv')
whitelist_path = os.path.join(os.path.dirname(__file__), 'Whitelist.json')

config = {      
    'Thumbnail'         : 'https://i.postimg.cc/XqQx5rT5/logo.png',
    'Link Overviewer'   : 'http://map.aeternumsmp.com:25581/',
    'Emoji Overviewer'  : '🌐',
    'Emoji Arrow Left'  : '⬅️',
    'Emoji Server'      : '<:aeternum:925134249865142303>',
    'Foundation Date'   : '2021-05-12',
    'Emoji Server'      : '<:aeternum:925134249865142303>',
    'IP Server'         : 'mc.aeternumsmp.com',
    'IP Plugins'        : 'plugins.aeternumsmp.com',
    'IP Dummy'          : 'dummy.aeternumsmp.com',
    'Ip 1.12'           : 'ae12.aeternumsmp.com',
    'IP Cobble'         : 'cobblemon.aeternumsmp.com',
    'Link Paypal'       : 'https://paypal.me/CubifyHosting',
    'Seed'              : '2563108827657901651',
    'Channel ID'        : 914533677411754024}
