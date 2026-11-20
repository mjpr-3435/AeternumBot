\gold\boldAETERNUM CARPET · GUÍA GENERAL\reset

Aeternum Carpet añade reglas y comandos propios a Carpet. Esta guía es la referencia rápida: indica qué hace cada regla, qué comandos habilita y quién puede usarlos.

\greenPARA TODOS\white significa cualquier jugador con acceso normal al comando. \redSOLO OP\white significa nivel de operador 2 o superior. Un comando solo existe mientras su regla esté activada.

—————————————————————————————————
\aqua\boldREGLAS: ACTIVAR, CONSULTAR Y GUARDAR\reset
—————————————————————————————————

\yellow/carpet <regla> <valor>\reset — \redSOLO OP\reset
Cambia una regla. Para reglas booleanas usa \yellowtrue\reset o \yellowfalse\reset.

\dark_grayEjemplo: /carpet commandFinder true

\yellow/carpet <regla>\reset — \redSOLO OP\reset
Muestra el valor y la descripción de una regla concreta.

\yellow/carpet list aeternum\reset — \redSOLO OP\reset
Muestra todas las reglas añadidas por Aeternum Carpet.

\yellow/rules\reset — \redSOLO OP\reset
Abre la interfaz visual para ver, buscar, filtrar y editar todas las reglas de Carpet y de sus extensiones, incluyendo restaurar al valor por defecto y guardar en la configuración del servidor. Requiere el cliente Aeternum Carpet.

Los cambios se guardan en la configuración de Carpet del servidor. Por defecto están activadas \yellowjoinMotd\reset, \yellownaturalIceFormation\reset y \yellowallowPlayerExploration\reset. Las herramientas de comandos y \yellowexplorationManager\reset empiezan apagadas.

—————————————————————————————————
\aqua\boldMECÁNICAS DIRECTAS\reset
—————————————————————————————————

\yellowspectatorPortalTravel\reset — apagada por defecto
Permite a jugadores en espectador atravesar portales como un jugador normal. La detección del portal funciona desde la altura de los ojos, así que volar de frente hacia un portal lo activa de inmediato. No da espectador ni cambia permisos; solo modifica ese comportamiento de los portales.

\yellowopenShulkerInHand\reset — apagada por defecto
Permite abrir una shulker al usarla en el aire mientras se sostiene en la mano. La mano principal tiene prioridad: si sostenés una shulker en la main hand, se abre sin importar qué tenga la offhand.

\yellow/quickshulker\reset — \greenPARA TODOS\reset
Activa o desactiva el acceso rápido de shulkers para quien ejecuta el comando. La regla debe estar activa; no afecta la preferencia de otros jugadores.

\yellowopenEnderChestInHand\reset — apagada por defecto
Permite abrir un cofre de Ender al usarlo en el aire mientras se sostiene en la mano. Igual que la shulker, la mano principal manda.

\yellow/quickenderchest\reset — \greenPARA TODOS\reset
Activa o desactiva el acceso rápido de cofres de Ender para quien ejecuta el comando. La regla debe estar activa.

Si tenés shulker en main hand y cofre de ender en offhand (o al revés), se abre lo que esté en la mano principal. La acción del otro ítem se cancela.

\yellowinstamineDeepslate\reset — apagada por defecto
Permite romper deepslate instantáneamente únicamente con pico de netherite, Eficiencia V y Prisa II o superior. No elimina los requisitos de herramienta ni altera los drops.

\yellowfastObsidian\reset — apagada por defecto
La obsidiana y obsidiana llorosa se rompen a la misma velocidad que la piedra con pico de netherite y Eficiencia V. No las instaminea: solo iguala el tiempo de rotura al de la piedra con las mismas herramientas. No requiere prisa.

\yellowbreakEndPortalFrames\reset — apagada por defecto
Permite romper marcos de portal del End mediante minería sostenida con maza, Breach IV, Prisa II y Fuerza II. Es una herramienta administrativa muy específica, no una rotura normal de marcos.

\yellowbreakEndPortalsWithWindCharge\reset — apagada por defecto
Permite que una carga de viento retire bloques de portal del End dentro de un área pequeña. Sirve para desmontar un portal activo sin editar archivos del mundo.

\yellowallowUnlimitedPlayerSpeed\reset — apagada por defecto
Desactiva la comprobación vanilla que retrocede a un jugador por moverse demasiado rápido. Úsala solo si una mecánica legítima del servidor necesita desplazamientos muy rápidos: también deja de aplicar esa protección de movimiento.

\yellownaturalIceFormation\reset — activada por defecto
Cuando está activa, el agua se congela naturalmente bajo las condiciones vanilla. En \yellowfalse\reset impide que se forme hielo natural; el hielo puesto por jugadores no se modifica.

\yellowprotectedPots\reset — apagada por defecto
Evita que los \yellowminecraft:decorated_pot\reset se rompan cuando un jugador colisiona con ellos volando con elytra impulsado por firework rocket. Las demás roturas (flechas, tridentes, explosiones, pistones y el minado manual) siguen funcionando como vanilla.

\yellowphantomSpawning\reset — valor por defecto: \yellowvanilla\reset
Controla la aparición natural de phantoms.

\dark_gray• \yellowvanilla\reset: comportamiento normal de Minecraft.
\dark_gray• \yellowmobcap\reset: los phantoms respetan el límite de mobs hostiles.
\dark_gray• \yellowdisable\reset: no aparecen phantoms naturalmente.

\yellowcraftableCalcite\reset — apagada por defecto
Habilita el crafteo de 2 bloques de calcita en mesa de crafteo o crafter usando 4 fragmentos de amatista en las esquinas, 4 de cuarzo del Nether en los bordes y 1 basalto liso en el centro.

—————————————————————————————————
\aqua\boldMENSAJE DE BIENVENIDA Y TAREAS\reset
—————————————————————————————————

\yellowjoinMotd\reset — activada por defecto
Muestra el banner de bienvenida al entrar y habilita los comandos siguientes.

\yellow/motd\reset — \greenPARA TODOS\reset
Vuelve a mostrar el banner de bienvenida personal.

\yellow/motd tasks\reset — \greenPARA TODOS\reset
Muestra las tareas públicas vigentes. No modifica nada.

\yellow/motd add <texto>\reset — \redSOLO OP\reset
Añade una tarea pública al banner. Se rechaza si está vacía, supera el límite o ya se alcanzó el máximo de tareas.

\yellow/motd delete <número>\reset — \redSOLO OP\reset
Elimina la tarea pública indicada. Después vuelve a mostrar la lista para confirmar el estado resultante.

—————————————————————————————————
\aqua\boldLISTA PERSONAL\reset
—————————————————————————————————

\yellowcommandTodoList\reset habilita \yellow/todo\reset. Las notas son personales: ni OP ni otros jugadores ven o modifican la lista de alguien más.

\yellow/todo\reset o \yellow/todo list\reset — \greenPARA TODOS\reset
Muestra tus notas numeradas. Cada línea incluye una X clicable para borrar esa nota.

\yellow/todo add <texto>\reset — \greenPARA TODOS\reset
Añade una nota a tu lista. El texto completo, incluidos espacios, se conserva como una sola nota.

\yellow/todo delete <número>\reset — \greenPARA TODOS\reset
Elimina una nota por su número y vuelve a mostrar la lista actualizada.

—————————————————————————————————
\aqua\boldGUÍAS DEL SERVIDOR\reset
—————————————————————————————————

\yellowcommandGuide\reset habilita \yellow/guide\reset. Las guías son archivos del mundo y el servidor es la fuente de verdad: los jugadores reciben el contenido al abrir el panel, no necesitan descargar una guía manualmente.

Las guías están organizadas por idioma en subdirectorios \yellowes/\reset y \yellowen/\reset dentro de \yellowworld/data/aeternum_guides\reset. Al abrir \yellow/guide\reset se carga el español por defecto. Los botones \yellow[ES]\reset y \yellow[EN]\reset en la esquina superior cambian entre idiomas.

\yellow/guide\reset — \greenPARA TODOS\reset
Abre la biblioteca de guías dentro del juego. Permite leer, desplazarse por textos largos, elegir otra guía y cambiar de idioma. Requiere el cliente Aeternum Carpet para mostrar la interfaz.

\dark_grayEn la biblioteca, los OP ven Editar y Refrescar; los demás solo leen.

\greenEN EL EDITOR — SOLO OP\reset

\dark_gray• Crear: crea una guía vacía con título único.
\dark_gray• Editar: el contenido se guarda automáticamente mientras se escribe.
\dark_gray• Renombrar: cambia el título y el archivo cuando hay un nombre nuevo pendiente.
\dark_gray• Reordenar: cada fila de la lista tiene ▲ y ▼ para subir o bajar una posición.
\dark_gray• Eliminar: borra la guía seleccionada (requiere mantener Shift).
\dark_gray• Refrescar: relee los archivos del servidor y detecta cambios hechos fuera del juego.

El botón ? muestra la ayuda de sintaxis dentro de la propia interfaz.

—————————————————————————————————
\aqua\boldPAQUETES DE ACCIONES\reset
—————————————————————————————————

\yellowcommandActions\reset habilita \yellow/actions\reset. Un paquete contiene pasos de comando y espera; los comandos se ejecutan como servidor, uno detrás de otro. Un paquete no puede duplicar el nombre de otro ignorando mayúsculas: \yellowBed\reset y \yellowbed\reset no son dos nombres válidos distintos.

\yellow/actions\reset — \greenPARA TODOS\reset
Abre la lista de paquetes. Todos pueden filtrar, revisar un paquete y ejecutar uno disponible. La ejecución avisa a todos los jugadores qué comando empezó, si terminó correctamente y si falló.

\yellow!!<nombre completo del paquete>\reset — \greenPARA TODOS\reset
Ejecuta directamente un paquete desde el chat. La coincidencia ignora mayúsculas y minúsculas; por ejemplo \yellow!!bedbot on\reset encuentra \yellowBedBot ON\reset. Debe escribirse el nombre completo después de \yellow!!\reset.

\redEN EL EDITOR — SOLO OP\reset

\dark_gray• Nuevo paquete: crea un paquete con nombre y descripción.
\dark_gray• Añadir línea: añade un paso de comando o de espera.
\dark_gray• Editar una línea: cambia la orden o la duración de la espera.
\dark_gray• Guardar: se activa solo si hay cambios pendientes; conserva la pantalla actual al guardar.
\dark_gray• Eliminar paquete o comando: requiere mantener Shift y ser OP.

Una espera usa segundos. Antes de guardar, revisa comandos destructivos, permisos, orden y destinatario: Actions no pide confirmación adicional cuando se ejecuta un paquete.

—————————————————————————————————
\aqua\boldMATERIALES: LISTAS DE RECOLECCIÓN DE PROYECTOS\reset
—————————————————————————————————

\yellowcommandMaterials\reset habilita \yellow/materials\reset. Las listas son archivos CSV en \yellowworld/data/aeternum_materials/\reset y comparan las cantidades objetivo contra lo almacenado y lo que lleva cada jugador.

\yellow/materials\reset — \greenPARA TODOS\reset
Abre las listas de materiales. La pantalla de detalle muestra cada ítem con su Total, su Falta y quién lo claimó.

\yellow/materials storage add <lista> <coord1> <coord2>\reset — \redSOLO OP\reset
Asigna la zona de almacenamiento de una lista. Cada lista tiene una única zona: si ya tiene una, el comando se rechaza hasta que se elimine.

\yellow/materials storage list\reset — \redSOLO OP\reset
Muestra las zonas de almacenamiento asignadas con una X clicable para eliminar una.

\yellow/materials storage del <lista> <índice>\reset — \redSOLO OP\reset
Elimina la zona de almacenamiento indicada.

La pantalla de detalle ordena los ítems en dos grupos: primero los faltantes y después los completados, ambos por total de mayor a menor. Las cantidades usan unidades progresivas: ítems sueltos, stacks (64 x N + Y), \yellowSB\reset (1 shulker = 1.728 ítems) y \yellowSDC\reset (un cofre doble de shulker boxes = 93.312 ítems).

El overlay del HUD muestra tus ítems claimados que todavía faltan; el conteo lo hace el servidor y también considera lo que llevás en tu inventario, incluidas las shulkers. Consultá la guía \whiteMateriales\dark_gray para el detalle completo.

—————————————————————————————————
\aqua\boldFINDER: BUSCAR EN ALMACENAMIENTOS\reset
—————————————————————————————————

\yellowcommandFinder\reset habilita Finder. Tiene dos niveles: consultas para todos y administración de zonas para OP. Finder no mueve ni modifica ítems. Cada consulta relee los contenedores antes de responder.

\yellow/find <lugar> <ítem>\reset — \greenPARA TODOS\reset
Busca el ítem en la zona indicada (con autocompletado de lugar) o en \yellownear_me\reset (radio de 20 bloques alrededor del jugador). Muestra cada contenedor coincidente, cantidad y coordenadas; para un jugador también marca una ruta temporal con partículas y marcadores.

\yellow/count <lugar> <ítem>\reset — \greenPARA TODOS\reset
Cuenta el total y los stacks del ítem en la zona indicada o en \yellownear_me\reset, sin enviar la ruta de partículas.

\yellow/finder scan <coord1> <coord2> <nombre>\reset — \redSOLO OP\reset
Crea o actualiza una zona (el nombre solo admite letras a-z, A-Z y números 0-9). Solo se escanean hasta 256 chunks y 10 000 000 bloques. El escaneo progresa incrementalmente sin partículas de vista previa.

\yellow/finder list\reset — \redSOLO OP\reset
Lista las zonas. Incluye botones chat: ↻ vuelve a escanear y X elimina la zona.

\yellow/finder remove <nombre>\reset — \redSOLO OP\reset
Elimina una zona registrada.

\yellow/finder check [coordenadas]\reset — \redSOLO OP\reset
Comprueba si un bloque es contenedor admitido y lo resalta.

\yellow/finder toggle-block [coordenadas]\reset — \redSOLO OP\reset
Incluye o excluye un bloque de todas las zonas que lo contienen.

\yellow/finder show_excludes\reset — \redSOLO OP\reset
Muestra los bloques excluidos de cada zona.

\yellow/finder clean\reset — \redSOLO OP\reset
Elimina todas las entidades \yellowminecraft:block_display\reset cargadas y limpia marcadores temporales de Finder.

—————————————————————————————————
\aqua\boldPROTECCIÓN DE BLOQUES\reset
—————————————————————————————————

\yellowcommandProtect\reset habilita \yellow/protect\reset. Es una protección persistente para bloques concretos, no un sistema de claims ni una región protegida completa.

\yellow/protect add [coordenadas]\reset — \redSOLO OP\reset
Protege el bloque mirado hasta seis bloques de distancia. Si se indican coordenadas, protege exactamente ese bloque. No permite proteger aire.

\yellow/protect remove [coordenadas]\reset — \redSOLO OP\reset
Quita la protección del bloque mirado o de las coordenadas indicadas.

\yellow/protect list\reset — \redSOLO OP\reset
Muestra todos los bloques protegidos, con dimensión y coordenadas.

—————————————————————————————————
\aqua\boldGESTIÓN DE EXPLORACIÓN\reset
—————————————————————————————————

\yellowexplorationManager\reset habilita \yellow/exploration\reset, sus regiones, la pregeneración y el mapa.

\yellow/exploration map\reset — \greenPARA TODOS\reset
Abre el mapa topográfico. Permite arrastrar para navegar, rueda para zoom, Espacio para volver a 0,0 y F para centrar la posición propia. Un solo botón \yellowDim\reset cicla entre Overworld, Nether y End. La barra superior muestra el MSPT del servidor en tiempo real. Requiere cliente Aeternum Carpet.

Los OP pueden crear regiones arrastrando con clic derecho sobre el mapa. La interfaz incluye botones para ajustar \yellowReq\reset (máximo de tiles simultáneos), \yellowLimpiar todo\reset (borrar caché de la dimensión) y \yellowLimpiar pantalla\reset (borrar solo los tiles visibles). Las regiones ahora son rectangulares: el arrastre define las esquinas, no un centro y radio.

\yellow/exploration pregen start\reset — \redSOLO OP\reset
Inicia o reanuda la cola de pregeneración de las regiones registradas. El progreso se conserva entre reinicios.

\yellow/exploration pregen pause\reset — \redSOLO OP\reset
Pausa la cola sin descartar el progreso.

\yellow/exploration pregen stop\reset — \redSOLO OP\reset
Detiene la cola y descarta su progreso guardado. Solo úsalo si se quiere empezar de nuevo.

\yellow/exploration pregen status\reset — \redSOLO OP\reset
Muestra estado, progreso y ritmo actual de pregeneración.

\yellow/exploration pregen speed <1-1200>\reset — \redSOLO OP\reset
Fija el máximo de chunks por minuto. El sistema no usa siempre ese máximo: trabaja solo con MSPT bajo y estable, por debajo de 20 ms, para no convertir picos de lag en carga adicional.

\yellowallowPlayerExploration\reset controla el límite de generación fuera de regiones. En \yellowtrue\reset permite explorar normalmente. En \yellowfalse\reset limita la generación a regiones registradas, siempre que el administrador de exploración no esté activo; mientras \yellowexplorationManager\reset funciona, esa barrera queda temporalmente desactivada para no interferir con gestión y pregeneración.

La selección se exporta automáticamente por dimensión para mantenimiento externo del mundo. No requiere un comando manual de exportación.

—————————————————————————————————
\aqua\boldAETERNUM DOCK, PROYECTOS Y PERÍMETROS\reset
—————————————————————————————————

\yellowquickDock\reset — apagada por defecto
Habilita el overlay \yellowAeternum Dock\reset en el cliente con accesos rápidos a pantallas del servidor, tareas del MOTD y selector de dimensión.

\yellowcommandProjects\reset — apagada por defecto
Habilita \yellow/projects\reset para gestionar proyectos del servidor, sus listas de materiales y archivos \yellow.litematic\reset vinculados.

\yellowcommandPerimeters\reset — apagada por defecto
Habilita \yellow/perimeter\reset (\redSOLO OP\reset) para registrar y monitorear perímetros de World Eater con alertas de altura Y objetivo, timeout de estancamiento y grilla de bots espectadores en \yellowY=128\reset.

—————————————————————————————————
\aqua\boldCALIDAD DE VIDA, BOTS Y ESTABILIDAD\reset
—————————————————————————————————

\yellowcameraMode\reset — valor por defecto: \yellowoff\reset (\yellowoff\reset, \yellowon\reset, \yellowrestrictive\reset)
Habilita \yellow/cs\reset (\greenPARA TODOS\reset) para alternar modo cámara/espectador temporal. En \yellowrestrictive\reset impide activarlo si estás en peligro (caída, fuego, lava, etc.).

\yellowcarefulBreak\reset — apagada por defecto
Habilita \yellow/carefulbreak <off|sneak|always>\reset (\greenPARA TODOS\reset) para mandar lo que minas directamente a tu inventario.

\yellowcommandHat\reset — apagada por defecto
Habilita \yellow/hat\reset (\greenPARA TODOS\reset) para equipar en la cabeza el ítem que llevas en la mano.

\yellowcommandDimension\reset — apagada por defecto
Habilita \yellow/nether\reset, \yellow/overworld\reset y \yellow/end\reset (\greenPARA TODOS\reset en Creativo o Espectador) para viajar rápidamente entre dimensiones.

\yellowplayerSit\reset — apagada por defecto
Permite sentarse en el lugar. Incluye \yellow/sitbehaviour clean armor_stands\reset (\redSOLO OP\reset) para limpiar armor stands huérfanos.

\yellowcommandViewInventory\reset — apagada por defecto
Habilita \yellow/viewinv <jugador>\reset (\redSOLO OP\reset) para inspeccionar el inventario de jugadores conectados o desconectados.

\yelloweditBotInventory\reset — apagada por defecto
Permite editar el inventario y cambiar el modo de juego de fake players desde su pantalla de inventario.

\yellowreloadFakePlayers\reset — apagada por defecto
Guarda los fake players activos antes de cerrar el servidor y los vuelve a conectar automáticamente al iniciar.

\yellowendermanGriefing\reset — valor por defecto: \yellowvanilla\reset (\yellowvanilla\reset, \yellowfarm_only\reset, \yellowdisable\reset)
Controla si los endermen pueden recoger o colocar bloques.

\yellowoldFlintAndSteelBehavior\reset — apagada por defecto
Restaura el comportamiento clásico del mechero al encender bloques.

\yellowupdateSuppressionCrashFix\reset — valor por defecto: \yellowfalse\reset (\yellowfalse\reset, \yellowtrue\reset, \yellowsilence\reset)
Evita que las excepciones de update suppression cierren el servidor (\yellowsilence\reset omite también los avisos en consola).

—————————————————————————————————
\aqua\boldKEYBINDS\reset
—————————————————————————————————

Aeternum Carpet registra en \yellowOpciones → Controles → Aeternum\reset el atajo de \yellowAeternum Dock\reset (por defecto \yellowAlt izquierdo\reset), que abre el dock rápido cuando \yellowquickDock\reset está activo.

—————————————————————————————————
\red\boldANTES DE CAMBIAR ALGO\reset
—————————————————————————————————

Las reglas simples pueden afectar a todos inmediatamente. Actions puede ejecutar comandos de servidor, Exploración puede generar muchos chunks y las herramientas administrativas cambian registros persistentes. Comprueba la regla activa, confirma el comando y haz el backup apropiado antes de cambios de mundo o automatizaciones importantes.
