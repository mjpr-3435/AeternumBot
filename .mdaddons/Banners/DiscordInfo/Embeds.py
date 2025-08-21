from .Modules import *

def apply_en_embed() -> list[discord.Embed]:
    embeds = [
        discord.Embed(
            title = 'Apply to the Server',
            colour = 0xDDF2FD,
            description = f'Joining Aeternum means you will become part of our internal community and gain access to our map, which is why we would like to get to know you better before allowing you access.'),
        discord.Embed(
            title ='Form',
            colour = 0x9BBEC8,
            description = (
                'To do this, we will ask you to fill out a form that you can access after creating a ticket using the `Tickets` button. '
                'Once you have submitted your form, you can use the ticket to answer the interviewers’ questions.\n\n'
                'Keep in mind that this is your first impression with us, and therefore it will weigh the most when deciding whether or not you are granted access to the server. '
                'We recommend that you take your time, answer carefully, elaborate as much as you can, and be honest when responding to the questions.\n\n'
                'It is important to note that you will not be able to join the server without having at least one voice conversation with us first. '
                'Therefore, having a microphone is mandatory in order to complete the process.\n\n'
                'We mainly look for people who are already somewhat familiar with the playstyle, although we do not require advanced knowledge unless you want to focus on redstone or building. '
                'What matters most to us is having a good time. Remember, this is not an exam.'
            ))]

    return embeds

def apply_es_embed() -> list[discord.Embed]:
    embeds = [
        discord.Embed(  
            title = 'Aplicar al servidor',
            colour = 0xDDF2FD,
            description = (
                'Ingresar a Aeternum significa que pasarás a ser parte de nuestra comunidad interna y que tendrás acceso a nuestro mapa, '
                'es por ello que nos gustaría conocerte mejor antes de permitirte ingresar a los mismos.'
            )
        ),
        discord.Embed(
            title = 'Formulario', 
            colour = 0x9BBEC8,
            description = (
                'Para ello, te pediremos que rellenes un formulario al cual podrás acceder luego de crear un ticket usando el botón `Tickets`. '
                'Una vez hayas enviado tu formulario, podrás usar el ticket para responder las preguntas de los entrevistadores.\n\n'
                'Ten en cuenta que esta es tu primera impresión hacia nosotros y, por tanto, es también la que pesará más al momento de decidir si te damos acceso o no al servidor. '
                'Te recomendamos que te tomes tu tiempo, que respondas con cuidado, que te explayes lo más que puedas y que seas sincero al responder las preguntas.\n\n'
                'Es importante señalar que no podrás ingresar al servidor sin antes tener al menos una conversación de voz con nosotros. '
                'Por lo tanto, es indispensable contar con micrófono para poder completar el proceso.\n\n'
                'Nosotros buscamos principalmente gente que ya conozca más o menos el estilo de juego, aunque no exigimos conocimientos avanzados salvo que quieras dedicarte a diseñar en redstone o decorar. '
                'Lo principal para nosotros es pasarla bien. Recuerda que esto no es un examen.'
            )
        )
    ]
    
    return embeds


def banner_en_embed():
    years = int(((datetime.today()-datetime.strptime(config['Foundation Date'], "%Y-%m-%d")).days)//365.25)
    days = int((datetime.today()-datetime.strptime(config['Foundation Date'], "%Y-%m-%d")).days%365.25)
    
    if years == 0:
        active_days = f'{days} days'
    elif days == 0:
        active_days = f'{years} years'
    else:
        active_days = f'{years} years {days} days'

    embed = discord.Embed(
            title = 'AeternumSMP',
            colour = 0x2f3136,
            description = 'Aeternum is a technical/decorative Minecraft server where our main goal is to have a good time.')\
        .add_field(name = 'Can I join Aeternum?', inline = False,value =
            'Certainly! Press the `Apply` button and follow the instructions.')\
        .add_field(name= 'Do you use mods in Aeternum?', inline = False, value =
            'We try to keep the game as close to vanilla as possible, however, we use carpet mod and some other optimization mods. If you want more information, press `Server Info`.')\
        .add_field(name = 'Discord Server Rules', inline = False, value = 
            'If it\'s your first time here, we invite you to press the `Rules` button and take a look at the server rules. We want all users to have a pleasant stay and avoid conflicts with each other.')\
        .add_field(name = 'Aeternum Links', inline = True, value =
            f'{config["Emoji Overviewer"]} [Overviewer]({config["Link Overviewer"]})\n'
            f'{config["Emoji YouTube"]} [YouTube]({config["Link YouTube"]})\n'
            f'{config["Emoji Patreon"]} [Patreon]({config["Link Patreon"]})\n'
            f'{config["Emoji Discord"]} [Discord]({config["Discord Invite"]})\n'
            f'{config["Emoji Twitter"]} [Twitter]({config["Link Twitter"]})\n'
            f'{config["Emoji TikTok"]} [TikTok]({config["Link TikTok"]})\n'
            f'{config["Emoji Twitch"]} [Twitch]({config["Link Twitch"]})\n')\
        .add_field(name = 'Information', inline = True, value=
            f'Active Time: {active_days}\n'
            f'Foundation: {config["Foundation Date"].replace("-","/")}\n'
            f'Version: Java 1.21.4\n'
            f'Premium: Yes\n')\
        .set_thumbnail(url = config['Thumbnail'])\

    return embed

def other_discords() -> discord.Embed :
    embed = discord.Embed(
        title="Otros Discords",
        color=0x2f3136,
    )

    for category, groups in friends_config['Discords'].items():
        items = list(groups.items())
        col1 = "\n".join(f"[{name}]({url})" for idx, (name, url) in enumerate(items) if idx % 3 == 0)
        col2 = "\n".join(f"[{name}]({url})" for idx, (name, url) in enumerate(items) if idx % 3 == 1)
        col3 = "\n".join(f"[{name}]({url})" for idx, (name, url) in enumerate(items) if idx % 3 == 2)

        embed.add_field(name=f"**{category}**", value=col1, inline=True)
        embed.add_field(name="\u200b", value=col2, inline=True)
        embed.add_field(name="\u200b", value=col3, inline=True)

        embed.add_field(name="", value="", inline=False)
    
    return embed


def members_embed() -> discord.Embed:
    df = pd.read_csv(members_list_path)

    df['display'] = df.apply(
        lambda row: (
            f"<:{row['member']}:{row['emoji_id']}> "
            f"[{row['member']}](https://discord.com/channels/839325517529612348/{row['thread_id']})"
            if row['thread_id'] != 0
            else f"<:{row['member']}:{row['emoji_id']}>"
        ),
        axis=1
    )

    embed = discord.Embed(
        title="Miembros",
        color=0x2f3136
    )

    col1 = "\n \n".join(df['display'][i] for i in range(len(df)) if i % 3 == 0)
    col2 = "\n \n".join(df['display'][i] for i in range(len(df)) if i % 3 == 1)
    col3 = "\n \n".join(df['display'][i] for i in range(len(df)) if i % 3 == 2)

    embed.add_field(name="", value=col1, inline=True)
    embed.add_field(name="", value=col2, inline=True)
    embed.add_field(name="", value=col3, inline=True)

    return embed

def autoroles_embed() -> discord.Embed:
    embed = discord.Embed(
        title = "Autoroles",
        description = 
            "Pulsa los botones de abajo para **suscribirte** o **desuscribirte** "
            "de las notificaciones de la categoría que quieras.",
        color = 0x2f3136
    )

    for nombre, descripcion in autoroles_categories.items():
        embed.add_field(name=nombre, value=descripcion, inline=True)
    embed.add_field(name='', value='', inline=True)

    return embed

def banner_es_embed() -> discord.Embed:
    years = int(((datetime.today()-datetime.strptime(config['Foundation Date'], "%Y-%m-%d")).days)//365.25)
    days = int((datetime.today()-datetime.strptime(config['Foundation Date'], "%Y-%m-%d")).days%365.25)
    
    if years == 0:
        active_days = f'{days} días'
    elif days == 0:
        active_days = f'{years} años'
    else:
        active_days = f'{years} años {days} días'

    embed = discord.Embed(
            title = 'AeternumSMP',
            colour = 0x2f3136,
            description = 'Aeternum es un servidor de Minecraft técnico/decorativo donde principalmente búscamos pasarla bien.')\
        .add_field(name = '¿Puedo entrar a Aeternum?', inline = False, value = 
            '¡Claro! Presiona el botón `Apply` y sigue las indicaciones.')\
        .add_field(name = '¿Usan mods en Aeternum?', inline = False, value =
            'Tratamos de mantener el juego lo más cercano al vanilla posible, sin embargo, usamos _carpet mod_ y otros mods de optimización. Si deseas más información presiona `Server Info`.')\
        .add_field(name = 'Reglas del servidor de Discord', inline = False, value = 
            'Si es tu primera vez por acá, te invitamos a que presiones el botón `Rules` y le des un vistazo a las reglas del servidor. Deseamos que todos los usuarios tengan una estadía agradable y evitar conflictos entre los mismos.')\
        .add_field(name = 'Links de Aeternum', inline = True, value =
            f'{config["Emoji Overviewer"]} [Overviewer]({config["Link Overviewer"]})\n'
            f'{config["Emoji YouTube"]} [YouTube]({config["Link YouTube"]})\n'
            f'{config["Emoji Patreon"]} [Patreon]({config["Link Patreon"]})\n'
            f'{config["Emoji Discord"]} [Discord]({config["Discord Invite"]})\n'
            f'{config["Emoji Twitter"]} [Twitter]({config["Link Twitter"]})\n'
            f'{config["Emoji TikTok"]} [TikTok]({config["Link TikTok"]})\n'
            f'{config["Emoji Twitch"]} [Twitch]({config["Link Twitch"]})\n')\
        .add_field(name = 'Información', inline = True, value =
            f'Tiempo activo: {active_days}\n'
            f'Fundación: {config["Foundation Date"].replace("-","/")}\n'
            f'Versión: Java 1.21.4\n'
            f'Premium: Sí\n')\
        .set_thumbnail(url = config['Thumbnail'])\
        .set_footer(text = 'English version available on `En` button.')

    return embed

def hardware_info_en_embed() -> discord.Embed:
    embed = discord.Embed(
            title = 'Aeternum Server',
            colour = 0x2f3136)\
        .add_field(name = '> Host Information', inline = False, value =
            '```asciidoc\n'
            'Type:: Dedicated Server\n'
            'Location:: Germany\n'
            'Processor:: i9-12900K\n'
            'Servers:: SMP/Mirror/CMP/Plugins'
            '```')\
        .add_field(name = '> Server Rules', inline = True, value =
            '- AccurateBlockPlacement\n'
            '- InstamineDeepslate\n'
            '- CombineXPOrbs\n'
            '- MissingTools\n'
            '- OptimizedTNT\n'
            '- ShadowItemsFix')\
        .add_field(name = '> Server Mods', inline = True, value =
            '- Syncmatica\n'
            '- EssentialCarefulBreak\n'
            '- Starlight\n'
            '- Lithium\n'
            '- PCA-Protocol')
    
    return embed

def hardware_info_es_embed() -> discord.Embed:
    embed = discord.Embed(
            title = 'Servidor de Aeternum',
            colour = 0x2f3136)\
        .add_field(name = '> Información sobre el host', inline = False, value = 
            '```asciidoc\n'
            'Tipo:: Servidor Dedicado\n'
            'Ubicación:: Alemania\n'
            'Procesador:: i9-12900K\n'
            'Servidores:: SMP/Mirror/CMP/Plugins'
            '```')\
        .add_field(name = '> Carpet Rules', inline = True, value = 
            '- AccurateBlockPlacement\n'
            '- InstamineDeepslate\n'
            '- CombineXPOrbs\n'
            '- MissingTools\n'
            '- OptimizedTNT\n'
            '- ShadowItemsFix')\
        .add_field(name = '> Server Mods', inline = True, value = 
            '- Syncmatica\n'
            '- EssentialCarefulBreak\n'
            '- Starlight\n'
            '- Lithium\n'
            '- PCA-Protocol')
    
    return embed

def rules_en_embed() -> list[discord.Embed]:
    embeds = [
        discord.Embed(
            title = 'Discord Server Rules',
            colour = 0xDDF2FD,
            description = 'We want everyone to have a pleasant stay on the server, so we have a set of rules that we hope you\'ll follow if you choose to remain here.'),
        discord.Embed(
            title = 'Voice Channels',
            colour = 0x9BBEC8,
            description ='Respect participants in the voice channels, avoid making unnecessary noise. It is recommended to steer clear of controversial topics such as politics or sports, in general, any subject that could generate disputes among participants.'),
        discord.Embed(
            title = 'Text Channels',
            colour = 0x427D9D,
            description = 'Respect participants in the text channels, avoid spamming, and refrain from sending sensitive content. Similarly, it is recommended to avoid controversial topics such as politics or sports, in general, any subject that could generate disputes among participants.'),
        discord.Embed(
            title = 'Terms and Conditions',
            colour = 0x164863,
            description = 'By participating in this server, you agree to the terms and conditions of Discord\'s service. You can find the terms and conditions on the following page [[Discord TOS]](https://discord.com/terms).')
            .set_footer(text='Violating any of these rules may result in your banning from the server.')]
    
    return embeds

def rules_es_embed() -> list[discord.Embed]:
    embeds = [
        discord.Embed(
            title = 'Reglas del servidor de Discord',
            colour = 0xDDF2FD,
            description = 'Deseamos que todos tengan una agradable estadía en el servidor, para ello tenemos una serie de reglas que esperamos que cumplas si permaneces en el mismo.'),
        discord.Embed(
            title = 'Canales de voz',
            colour = 0x9BBEC8,
            description = 'Respetar a los participantes de los canales de voz, no hacer bulla innecesariamente. Se recomienda evitar temas polémicos como la política o el deporte, en general, cualquier tema que pueda generar controversias entre los participantes.'),
        discord.Embed(
            title = 'Canales de texto',
            colour = 0x427D9D,
            description = 'Respetar a los participantes de los canales de texto, no hacer spam, no mandar contenido sensible. De igual forma, se recomienta evitar los temas polémicos como la política o el deporte, en general, cualquier tema que pueda generar controversias entre los participantes.'),
        discord.Embed(
            title = 'Terminos y condiciones',
            colour = 0x164863,
            description = 'Al participar en este servidor, aceptas los términos y condiciones del servicio de Discord. Los términos y condiciones los puedes encontrar en la siguiente página [[Discord TOS]](https://discord.com/terms).')\
            .set_footer(text='Incumplir cualquiera de estas normas puede conllevar a tu baneo del servidor.')]
    
    return embeds
