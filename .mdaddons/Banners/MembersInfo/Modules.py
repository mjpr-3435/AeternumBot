import pandas as pd
import numpy as np
import discord
import asyncio
import traceback
import os
import sys

from mcdis_rcon.utils import isAdmin, thread
from mcdis_rcon.classes import McDisClient

from discord.app_commands import describe, choices, Choice
from discord.ext import commands
from datetime import datetime

tasks_log = os.path.join(os.path.dirname(__file__), 'TasksLog.csv')

config = {      
    'Thumbnail'         : 'https://i.postimg.cc/XqQx5rT5/logo.png',
    'Emoji Server'      : '<:aeternum:925134249865142303>',
    'Foundation Date'   : '2021-05-12',
    'IP Server'         : 'smp.ip',
    'IP Plugins'        : 'plugins.ip',
    'Ip 1.12'           : 'ae12.ip',
    'Seed'              : '2563108827657901651',
    'Channel ID'        : 1341217034498998344}
