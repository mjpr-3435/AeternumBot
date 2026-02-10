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

def patreon_embed() -> discord.Embed:
    embed = discord.Embed(
        title="Apóyanos en Patreon",
        description="Si te gusta Aeternum y quieres ayudarnos a mantener y mejorar el servidor, puedes apoyarnos en Patreon. ¡Cada aporte cuenta!",
        colour=0xFF424D
    )
    embed.set_image(url="https://media.discordapp.net/attachments/1363023389681385544/1425632876287889612/image.png?ex=68e84b94&is=68e6fa14&hm=3ca4fb3ed3174ba4912ba856e7b8e74f85633d732f245733ef277de8439f58d4&=&format=webp&quality=lossless&width=1524&height=800")
    embed.set_footer(text="Gracias por apoyar a Aeternum ❤️")

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


def patreon_embed() -> discord.Embed:
    years = (datetime.today() - datetime.strptime(config['Foundation Date'], "%Y-%m-%d")).days / 365.25
    active_days = f"{years:.1f} años"


    embed = discord.Embed(
        title="Aeternum Patreon",
        description=f"""
Si quieres ayudarnos a mantener y mejorar el servidor, puedes apoyarnos en `Patreon`. Allí encontrarás diferentes opciones que podrían interesarte:

- **Aecademy:** acceso a un servidor de enseñanza, con el mismo estilo que nuestro SMP, pensado para aprender Minecraft técnico.
- **Maparts personalizados:** envíanos una imagen y la convertimos en un mapart dentro de nuestro mundo.  
- **Reinicio del mundo:** puedes comprar el mapa actual ({active_days} de desarrollo) y nosotros comenzamos uno nuevo desde cero.  
- **Tours privados:** recorridos guiados por nuestro mapa principal, con decoraciones y redstone avanzada.  
- **Hosting:** servidores configurados como el nuestro, listos para que montes tu propio servidor técnico.

Puedes ver los detalles de cada opción en nuestro Patreon o en el menú desplegable de abajo.

[{config['Emoji Patreon']} [Aeternum Patreon]]({config['Link Patreon']})""",
        colour=0x2f3136
    )
    embed.set_image(url=config["Image Patreon"])

    return embed

def embed_aecademy() -> discord.Embed:
    embed = discord.Embed(
        title="Aecademy (3.5$ - 12$)",
        description=(
            "Aecademy es un servidor privado con el mismo estilo que nuestro SMP principal. "
            "Está orientado a jugadores que desean aprender Minecraft técnico desde cero y conocer a otros con quienes formar su propio SMP. "
            "El mapa se reinicia cada año y, al finalizar la temporada, se entrega una copia completa a todos los miembros activos de Aecademy.\n\n"
            "El acceso es gratuito durante el primer mes y luego pasa a ser de pago; puedes adquirir cupos a través de nuestro Patreon.\n\n"
            "Pueden encontrar información más detallada en el canal dedicado a Aecademy, <#1423058606382645489>."
        ),
        colour=0x2f3136
    )
    return embed


def embed_maparts() -> discord.Embed:
    embed = discord.Embed(
        title="Maparts personalizados (5$ - 20$)",
        description=(
            "Puedes enviarnos cualquier imagen, y nosotros la convertimos en un `Mapart` dentro de nuestro mundo. "
            "El proceso se realiza manualmente, con materiales obtenidos en survival técnico. "
            "Es una forma de dejar tu marca dentro de Aeternum."
        ),
        colour=0x2f3136
    )
    return embed


def embed_tours() -> discord.Embed:
    embed = discord.Embed(
        title="Tours privados (8$ - 15$)",
        description=(
            "Ofrecemos recorridos guiados por nuestro mapa principal. "
            "Durante el tour mostramos sistemas de redstone complejos, granjas, decoración y áreas históricas del servidor. "
            "Ideal para quienes quieren conocer cómo funciona Aeternum por dentro."
        ),
        colour=0x2f3136
    )
    return embed

def embed_hosting() -> discord.Embed:
    embed = discord.Embed(
        title="Aeternum Hosting (16$ - 40$)",
        description=(
            "Cada plan ofrece acceso a un usuario en un servidor dedicado ubicado en Finlandia (**CPU i9-12900K**) "
            "con **8GB, 12 GB o 24 GB de RAM** según el plan.\n\n"

            "**Beneficios por defecto:**\n"
            "El entorno viene completamente configurado y listo para usar:\n"
            "- Dos servidores preconfigurados (**SMP** y **CMP**).\n"
            "- **MCDReforged** instalado en cada servidor.\n"
            "- Servidores enlazados mediante **BungeeCord**.\n"
            "- Panel de administración desde Discord **McDis RCON**.\n"
            "Es posible tener más servidores preconfigurados mientras se mantenga el uso de **RAM** dentro del límite contratado.\n\n"

            "**Beneficios técnicos adicionales:**\n"
            "- Acceso completo por **SFTP** para gestión de archivos.\n"
            "- Posibilidad de usar **bash** directamente en el dedicado para revisar, modificar o monitorear el entorno a tu gusto.\n\n"
        ),
        colour=0x2f3136
    ).add_field(
        name="> Nota:",
        value=(
            "Por defecto no se incluyen plugins de **MCDReforged** (solo `Quick Backups` y `Timed Backups`). "
            "El usuario puede agregar y configurar sus propios plugins.\n\n"
            "El panel **McDis RCON** viene incluido y totalmente funcional; los plugins adicionales son opcionales y se cobran aparte."
        ),
        inline=False
    )

    
    return embed

def embed_reboot() -> discord.Embed:
    years = (datetime.today() - datetime.strptime(config['Foundation Date'], "%Y-%m-%d")).days / 365.25
    active_years = f"{years:.1f} años"

    embed = discord.Embed(
        title="Compra del mapa actual (4000$)",
        description=(
            f"Nuestro mundo actual tiene aproximadamente **{active_years} de desarrollo**. "
            "Ofrecemos la posibilidad de comprar una copia completa del mapa y, tras ello, "
            "comenzamos un nuevo mundo desde cero.\n\n"
            "Sí, cuesta alrededor de `4000$`, así que más que una propuesta seria es un capricho para quien no sepa qué hacer con su dinero."
        ),
        colour=0x2f3136
    )
    return embed


def aecademy_embed() -> list[discord.Embed]:
    color_base = 0x2F3136
    embeds = []

    general = discord.Embed(
        title="**Aecademy SMP**",
        colour=color_base,
        description=(
            "Aecademy es un servidor `por temporadas` cuyo objetivo es enseñar a las personas cómo organizar su propio servidor técnico. "
            "El servidor está **Java 1.21.4**  y es para jugadores con el **Minecraft Premium**.\n\n"
            "El mapa se reinicia `cada año` y, al final de la temporada, se le entregará "
            "a todos los participantes que permanezcan hasta el último mes un enlace de descarga del mismo. "
            "Con ese mapa podrán decidir si iniciar su propio SMP o continuar independientemente.\n\n"
        )
    ).add_field(
        name="**¿Cómo entrar en Aecademy?**",
        value=(
            "Aecademy es gratuito durante el primer mes de la temporada. "
            "Luego, para continuar participando, se debe apoyar al servidor de alguna manera, "
            "ya sea a través de Patreon o realizando un boost al servidor de Discord. "
            "Para más información selecciona `Beneficios` en el desplegable.\n\n"
            "`       Fecha de inicio: 01 de noviembre de 2025       `\n\n" 
            f"{config['Emoji Patreon']} [[Aeternum Patreon]]({config['Link Patreon']})"
            ),
        inline=False
    ).set_image(
        url=config['Image Patreon']
    )

    embeds.append(general)
    return embeds

def beneficios_embed() -> list[discord.Embed]:
    embeds = []
    beneficios_generales = discord.Embed(
        title="🎓 Beneficios de participar en Aecademy",
        colour=0x2f3136,
        description=(
            "Antes de acceder a cualquiera de los beneficios o realizar una suscripción, "
            "es fundamental que leas los apartados de **Términos de Servicio** y **Aprendizaje y Moderación** "
            "en el menú principal de información.\n\n"
            "Al realizar una compra o suscripción, se asume que el participante **ha leído y acepta** "
            "los términos y condiciones que implican participar en Aecademy.\n\n"
            "A continuación se detallan los beneficios disponibles:"
        )
    )
    beneficios_generales.add_field(
        name="🧩 **Beneficios generales**",
        value=(
            "- Whitelistear gente en el servidor de Aecademy.\n"
            "- El servidor de Aecademy incluye dos instancias: `SMP` y `CMP`, cada una con `6GB` de `RAM`, igual que los servidores de Aeternum.\n"
            "- Ambos servidores funcionan en la misma network usando `Velocity`.\n"
            "- Hardware de alto rendimiento con procesador `i9-12900K`, el mismo que el servidor principal de Aeternum. Los servidores están alojados en Alemania.\n"
            "- Servidores ya configurados con mods de optimización y Carpet Mod utilizados habitualmente.\n"
            "- Mapas preparados para sus objetivos específicos.\n"
            "- MCDReforged configurado.\n"
            "- McDis configurado."
        ),
        inline=False
    )

    beneficios_generales.add_field(
        name=f"{config['Emoji Patreon']} **Roles de acceso**",
        value=(
            "Puedes apoyar a Aeternum a través de `Patreon` o `boosteando` el servidor de Discord. "
            "Al hacerlo, recibirás automáticamente un rol que te otorga la posibilidad de **añadir jugadores** a la whitelist de Aecademy "
            "y acceder a los beneficios mencionados en la sección anterior.\n\n"
            "Cada nivel de apoyo ofrece ventajas distintas:"
            ),
        inline=False
    )

    for rol, cantidad in supporter_permissions.items():
        role_id = next((rid for rid, name in supporter_roles.items() if name == rol), None)

        beneficios_generales.add_field(
            name='',
            value=f'<@&{role_id}>\nPermite añadir hasta **{cantidad}** jugador{"es" if cantidad > 1 else ""}.\nPrecio: `{prices[rol]}` 💸',
            inline=True
        )

    beneficios_generales.set_footer(
        text=(
            "📌 Los beneficios son acumulativos: por ejemplo, si tienes Server Booster (1) y Patreon Tier 2 (2), "
            "podrás añadir un total de 3 jugadores.\n\n"
            "⚠️ En el caso de Server Booster, no se otorgan beneficios adicionales por hacer varios boosts desde la misma cuenta."
        )
    )
    
    embeds.append(beneficios_generales)

    return embeds

def tos_embed() -> list[discord.Embed]:
    embeds = []

    tos = discord.Embed(
        title="Términos de Servicio",
        colour=0x2f3136,
        description=(
            "Por favor, lee cuidadosamente los siguientes términos antes de participar en Aecademy.\n\n"
            "El uso del servidor de Aecademy (Discord y Minecraft) implica la aceptación de estas normas y condiciones. "
        )
    )

    tos.add_field(
        name="**1. Comportamiento y respeto**",
        value=(
            "- Está prohibido cualquier tipo de acoso, discriminación o comportamiento tóxico.\n"
            "- Respeta a todos los miembros y al staff en todo momento.\n"
            "- Las bromas están permitidas siempre que sean consensuadas."
        ),
        inline=False
    )

    tos.add_field(
        name="**2. Contenido y comunicación**",
        value=(
            "- No publicar contenido NSFW o inapropiado en el servidor.\n"
            "- Respeta los canales y utiliza el chat para su propósito correspondiente.\n"
            "- El acceso a Aecademy requiere tener **Minecraft Premium (Java Edition)**."
        ),
        inline=False
    )

    tos.add_field(
        name="**3. Formación especializada**",
        value=(
            "No ofrecemos clases ni respondemos preguntas de manera arbitraria, ni actuamos como un asistente automático. "
            "Podemos brindarte orientación dentro de nuestros conocimientos, con recursos y guías para que te apoyes en tu aprendizaje.\n\n"
            "`Redstone`: Orientación general, compartimos videos, guías, materiales y podemos evaluar tus diseños terminados.\n"
            "`Construcción`: Consejos sobre plugins o herramientas de Axiom útiles para proyectos, además de sugerir videos y guías.\n\n"
            "La interacción es flexible siempre que las preguntas sean razonables y tengan sentido, pero no responderemos repetidamente preguntas que se puedan resolver consultando los recursos proporcionados."
        ),
        inline=False
    )

    tos.add_field(
        name="**4. Moderación y advertencias**",
        value=(
            "- Se aplican 3 advertencias antes de cualquier sanción.\n"
            "- Mantén respeto y buenas prácticas en todo momento."
        ),
        inline=False
    )

    tos.add_field(
        name="**5. Modificaciones y cambios**",
        value=(
            "- El staff se reserva el derecho de modificar las normas y el servidor.\n"
            "- Los cambios menores podrán aplicarse en cualquier momento.\n"
            "- Los cambios importantes se notificarán con un mes de anticipación a los miembros involucrados, y la permanencia en el servidor implicará su aceptación."
        ),
        inline=False
    )

    tos.add_field(
        name="**6. Pagos y reembolsos**",
        value=(
            "- El acceso a los beneficios de Aecademy está sujeto a la suscripción activa en Patreon o a la permanencia del Boost de Discord.\n"
            "- Dicho pago es final y no se realizan devoluciones bajo ningún concepto, independientemente del tiempo de uso."
        ),
        inline=False
    )

    tos.set_footer(
        text="El incumplimiento de estos términos puede resultar en sanciones, incluyendo expulsión del servidor."
    )

    embeds.append(tos)

    return embeds

def info_aprendizaje_embed() -> list[discord.Embed]:
    color_base = 0x2F3136
    embeds = []

    aprendizaje = discord.Embed(
        title="**¿Qué esperar de Aecademy SMP?**",
        colour=color_base,
        description=(
            "En Aecademy no solo jugarás, sino que aprenderás las bases para gestionar tu propio servidor técnico. "
            "Durante la temporada trabajaremos juntos en distintos proyectos y roles prácticos."
        )
    ).add_field(
        name="**Metas al finalizar la temporada**",
        value=(
            "- Aprender métodos para abrir perímetros y comprender las mecánicas básicas del juego.\n"
            "- Aprender a organizar y gestionar proyectos.\n"
            "- Manejar mods de Masa como `MiniHUD`, `Tweakeroo`, `Litematica`, entre otros, así como las variantes del `Carpet Mod`.\n"
            "- Contar con las granjas esenciales y un Main Storage plenamente funcional.\n"
            "- Formar un grupo con la capacidad de administrar un SMP a partir del mapa entregado."
        ),
        inline=False
    ).add_field(
        name="**Moderadores y administración**",
        value=(
            "Los participantes que demuestren compromiso y ganen la confianza del staff podrán ascender a moderadores. "
            "Esto incluye aprender a configurar y administrar el servidor, manejar la network, "
            "usar MCDReforged, instalar plugins, trabajar con el panel McDis y crear un bot de Discord "
            "para mantener un servidor funcional y atractivo."
        ),
        inline=False
    ).add_field(
        name="**Conexión con Aeternum**",
        value=(
            "Además, compartiremos nuestras experiencias en la administración de `Aeternum` como referencia. "
            "Los miembros de Aeternum también ingresarán ocasionalmente a Aecademy para colaborar en distintas actividades."
        ),
        inline=False
    ).add_field(
        name="**Acceso al servidor principal de Aeternum**",
        value=(
            "Participar en Aecademy también brinda un acceso más directo al servidor principal de Aeternum, "
            "ya que durante la temporada iremos conociendo a los miembros y evaluando su desempeño."
        )
    )

    embeds.append(aprendizaje)
    return embeds
