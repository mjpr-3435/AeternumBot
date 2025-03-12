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
            description =
                f'To do this, we will ask you to fill out a form which you can access by pressing the `Tickets` button. Once you have submitted your form, you will be able to use the ticket to respond to the interviewers\' questions.\n\n'
                f'Keep in mind that this is your first impression on us and, therefore, it is also the one that will carry the most weight when deciding whether to grant you access to the server. We recommend that you take your time, answer carefully, and try to elaborate as much as possible in your responses.')]

    return embeds

def apply_es_embed() -> list[discord.Embed]:
    embeds = [
        discord.Embed(
            title = 'Aplicar al servidor',
            colour = 0xDDF2FD,
            description = f'Ingresar a Aeternum significa que pasarás a ser parte de nuestra comunidad interna y que tendrás acceso a nuestro mapa, es por ello que nos gustaría conocerte mejor antes de permitirte ingresar a los mismos.'),
        discord.Embed(
            title = 'Formulario', 
            colour = 0x9BBEC8,
            description = 
                f'Para ello, te pediremos que rellenes un formulario al cual podrás acceder luego de crear un ticket usando el boton `Tickets`. Una vez hayas enviado tu formulario, podrás usar el ticket para responder las preguntas de los entrevistadores.\n\n'
                f'Ten en cuenta que esta es tu primera impresión hacia nosotros y, por tanto, es también la que pesará más al momento de dirimir si te damos acceso o no al servidor. Te recomendamos que te tomes tu tiempo, que respondas con cuidado y que trates de explayarte lo más que puedas en tus respuestas.')]
    
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
            description = 'Aeternum is a technical/decorative Minecraft server where we aim to have a good time and undertake great projects.')\
        .add_field(name = 'Can I join Aeternum?', inline = False,value =
            'Certainly! Press the `Apply` button and follow the instructions.')\
        .add_field(name= 'Do you use mods in Aeternum?', inline = False, value =
            'We try to keep the game as close to vanilla as possible, however, we use carpet mod and some other optimization mods. If you want more information, press `Server Info`.')\
        .add_field(name = 'Discord Server Rules', inline = False, value = 
            'If it\'s your first time here, we invite you to press the `Rules` button and take a look at the server rules. We want all users to have a pleasant stay and avoid conflicts with each other.')\
        .add_field(name = 'Aeternum Links', inline = True, value =
            f'{config["Emoji Overviewer"]} [Overviewer]({config["Link Overviewer"]})\n'
            f'{config["Emoji YouTube"]} [YouTube]({config["Link YouTube"]})\n'
            f'{config["Emoji Discord"]} [Discord]({config["Discord Invite"]})\n'
            f'{config["Emoji Twitter"]} [Twitter]({config["Link Twitter"]})\n'
            f'{config["Emoji Twitch"]} [Twitch]({config["Link Twitch"]})\n')\
        .add_field(name = 'Information', inline = True, value=
            f'Active Time: {active_days}\n'
            f'Foundation: {config["Foundation Date"].replace("-","/")}\n'
            f'Version: 1.20.1\n')\
        .set_thumbnail(url = config['Thumbnail'])\

    return embed

def banner_es_embed():
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
            description = 'Aeternum es un servidor de Minecraft técnico/decorativo donde búscamos pasarla bien y llevar a cabo grandes proyectos.')\
        .add_field(name = '¿Puedo entrar a Aeternum?', inline = False, value = 
            '¡Claro! Presiona el botón `Apply` y sigue las indicaciones.')\
        .add_field(name = '¿Usan mods en Aeternum?', inline = False, value =
            'Tratamos de mantener el juego lo más cercano al vanilla posible, sin embargo, usamos _carpet mod_ y otros mods de optimización. Si deseas más información presiona `Server Info`.')\
        .add_field(name = 'Reglas del servidor de Discord', inline = False, value = 
            'Si es tu primera vez por acá, te invitamos a que presiones el botón `Rules` y le des un vistazo a las reglas del servidor. Deseamos que todos los usuarios tengan una estadía agradable y evitar conflictos entre los mismos.')\
        .add_field(name = 'Links de Aeternum', inline = True, value =
            f'{config["Emoji Overviewer"]} [Overviewer]({config["Link Overviewer"]})\n'
            f'{config["Emoji YouTube"]} [YouTube]({config["Link YouTube"]})\n'
            f'{config["Emoji Discord"]} [Discord]({config["Discord Invite"]})\n'
            f'{config["Emoji Twitter"]} [Twitter]({config["Link Twitter"]})\n'
            f'{config["Emoji Twitch"]} [Twitch]({config["Link Twitch"]})\n')\
        .add_field(name = 'Información', inline = True, value =
            f'Tiempo activo: {active_days}\n'
            f'Fundación: {config["Foundation Date"].replace("-","/")}\n'
            f'Versión: 1.20.1\n')\
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
