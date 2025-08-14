import discord
import asyncio
import traceback
import aiohttp
import os

from discord.app_commands import describe, choices, Choice
from discord.ext import commands
from mcdis_rcon.classes import McDisClient
from discord.ext import commands
from datetime import datetime
from typing import Union
import pandas as pd

tickets_log = f'{os.path.dirname(__file__)}/TicketSystem/TicketsLog.csv'
form_log = f'{os.path.dirname(__file__)}/Form/FormsLog.csv'
members_list_path = f'{os.path.dirname(__file__)}/MembersList.csv'
blacklist = []

autoroles_categories = {
    "📅 Eventos"        : "Recibe avisos sobre próximos eventos.",
    "<:AeTwitch:1390864664791093319> Twitch": "Sé notificado cuando haya transmisiones en vivo.",
    "🎊 Nuevo Contenido": "Publicaciones de proyectos terminados, cinemáticas, TikToks o tours.",
    "📌 Anuncios"       : "Recibe información importante del servidor.",
    "📮 Todo"           : "Obtén notificaciones de todas las categorías anteriores."
    }

autoroles_ids = {
    "eventos"           : 1404096972612309022,
    "twitch"            : 1404096918283620472,
    "nuevo_contenido"   : 1404097158403326096,
    "anuncios"          : 1404097152732627057,
    "todo"              : 1404097166321913999
}

config = {      
    'Thumbnail'         : 'https://i.postimg.cc/XqQx5rT5/logo.png',
    'Discord Invite'    : 'https://discord.gg/pXwV7BWd2P',
    'Link YouTube'      : 'https://www.youtube.com/channel/UCjjMAJirU2oWOrQPwGsDxYw',
    'Link Patreon'      : 'https://www.patreon.com/Aeternum_SMP',
    'Link Twitter'      : 'https://twitter.com/aeternum_smp',
    'Link Twitch'       : 'https://www.twitch.tv/aeternumsmp',
    'Link Overviewer'   : 'http://map.aeternumsmp.com:25581/',
    'Link TikTok'       : 'https://www.tiktok.com/@aeternumsmp7',
    'Emoji Server'      : '<:aeternum:925134249865142303>',
    'Emoji Discord'     : '<:AeDiscord:1390864678540017739>',
    'Emoji YouTube'     : '<:AeYoutube:1390864688425865296>',
    'Emoji Twitch'      : '<:AeTwitch:1390864664791093319>',
    'Emoji Twitter'     : '<:AeTwitter:1390864699255427173>',
    'Emoji Patreon'     : '<:AePatreon:1390869116755382353>',
    'Emoji TikTok'      : '<:AeTikTok:1403595577895161978>',
    'Emoji Overviewer'  : '🌐',
    'Foundation Date'   : '2021-05-12',
    'Channel ID'        : 866452465879744532}
    
config_form = {      
    'Thumbnail'     : 'https://i.postimg.cc/XqQx5rT5/logo.png',
    'Emoji Yes'     : '<:PepeYes:887447915289776159>',
    'Emoji No'      : '<:PepeNo:887447914291560468>',
    'Channel ID'    : 892445483472142346
    }

tickets_config = {      
    'Category ID'   : 1391118984056799403,
    'Ticket Moderator ID' : 914530780523401267
    }

friends_config = {
    'Discords': {
        'Personales': {
            '<:CarsomDs:1403597358914207744> Purple Ribbon' : 
            'https://discord.gg/edbaXCDnpK',

            '<:SheronDs:1403597368535810143> El Archivador de Sheron' : 
            'https://discord.gg/k96nwRhWUS',

            '<:CopraDs:1403597378656665741> The Copratox Channel'  : 
            'https://discord.gg/Hkmgh2tUba',

            '<:KisdeDs:1403597347824341033> Kisde House' : 
            'https://discord.gg/x6PdsQNfcf',

            '<:PepiDs:1403597400618303549> Pepi' :
            'https://discord.gg/cJPD7QRvMz'
        },
        'Archivos': {
            '<:Signature:1403597391231455232> Signature Group' :
            'https://discord.gg/qx2rHk6TtV',

            '<:TMCB:1403597338399998122> TMC Decorators' :
            'https://discord.gg/ewEk6H2kSF',

            '<:MTDR:1403599113672593528> Discord Recollector' :
            'https://discord.gg/UT8ns46As9',

            '<:MMM:1403597293197856839> Manual Minig Maniacs' :
            'https://discord.gg/U2vQ93wWZ9',

            '<:Records:1403597283878109265> Leaderboard Archive' :
            'https://discord.gg/CBxh2mdebV'
        },
        'SMPs': {
            '<:CTEC:1403597417047265320> CTEC':
            'https://discord.gg/H6uHghNq5Z',
            
            '<:Minewave:1403597330380357773>MineWave' :
            'https://discord.gg/keyy8As',

            '<:Sigma:1403597320754561134> Sigma' :
            'https://discord.gg/ScBwSAuxSF',

            '<:CraftersHub:1403597311900127232> Crafters Hub' :
            'https://discord.gg/uNdAXPMQkG',

            '<:Bullet:1403597303679418531> Bullet' :
            'https://discord.gg/PXRBwWXqGc'
        }
    }
}
