\gold\boldEXPLORACIÓN Y PREGENERACIÓN\reset

El Exploración Manager reúne cuatro cosas: regiones permitidas, pregeneración gradual, exportación de la selección para herramientas externas y un mapa topográfico del mundo ya generado.

Administración debe activar \yellowexplorationManager\reset para habilitar \yellow/exploration\reset. El sistema guarda sus regiones y su configuración en el servidor; el mapa y sus datos vienen del servidor, no del cliente.

—————————————————————————————————
\aqua\boldCONCEPTOS IMPORTANTES\reset
—————————————————————————————————

Una región tiene nombre, dimensión y un rectángulo de chunks definido por esquinas mínima y máxima. Ya no se usa un centro con radio: ahora podés crear regiones no cuadradas (por ejemplo, 10 × 3 chunks).

Las regiones no borran ni crean bloques por sí mismas. Son una selección administrativa que puede servir para limitar exploración, exportar CSV y alimentar la pregeneración.

Los nombres son únicos y solo admiten letras, números, _ y -. Una región siempre pertenece a la dimensión donde se creó.

—————————————————————————————————
\green\boldPARA TODOS: MAPA\reset
—————————————————————————————————

\yellow/exploration map\reset
Abre el mapa topográfico. Muestra terreno que ya está guardado en el mundo, con un píxel de color por bloque y regiones permitidas en naranja. Abrirlo o navegarlo no genera chunks: el servidor lee los archivos de región existentes y construye una caché reutilizable.

\aqua\boldNAVEGACIÓN\reset

\dark_gray• Arrastra con clic izquierdo para mover la vista.
\dark_gray• Usa la rueda para acercar o alejar. El zoom va de 0.0625× a 16× y conserva el punto bajo el cursor.
\dark_gray• Pulsa Espacio para volver a 0,0 y zoom 1×.
\dark_gray• Pulsa F para centrar la vista en tu posición actual.
\dark_gray• El botón \yellowDim\reset cicla entre Overworld, Nether y End.
\dark_gray• Chunks y Regiones activan sus cuadrículas. Ambas empiezan desactivadas.

La barra superior muestra el MSPT del servidor en tiempo real, el título y la dimensión, y las coordenadas de bloque, chunk y archivo de región bajo el cursor. Los botones de cuadrícula no cambian el mundo: solo ayudan a medir y orientarse.

El mapa entrega datos a escala 1:1: un bloque corresponde a un píxel de color. No mezcla el mapa según el zoom. En Nether y End toma la superficie real más alta disponible, incluso construcciones sobre el techo.

Una zona gris normalmente significa que todavía no existe un chunk guardado o que el tile aún está llegando; no significa que el mapa haya generado terreno nuevo.

\aqua\boldBOTONES DE ADMINISTRACIÓN\reset

Los OP ven tres botones adicionales en la barra inferior:

\dark_gray• \yellowReq\reset: controla cuántos tiles puede pedir tu cliente a la vez. Click para ciclar 4 → 8 → 16 → 32 → 48 → 64. Menos tiles = menos carga instantánea, más lento de llenar.
\dark_gray• \yellowLimpiar todo\reset: borra toda la caché del mapa de la dimensión actual (memoria y disco). Los tiles se recalcularán al volver a pedirlos.
\dark_gray• \yellowLimpiar pantalla\reset: borra solo los tiles que estás viendo. Útil para forzar una actualización visual sin limpiar todo.

Al clickear cualquiera de estos botones, se desactivan momentáneamente (parpadeo) y se reactivan solos, confirmando que la acción se envió.

—————————————————————————————————
\red\boldSOLO ADMINISTRACIÓN: REGIONES\reset
—————————————————————————————————

\aqua\boldCREAR DESDE EL MAPA\reset

Hacé clic derecho sobre el mapa y arrastrá para dibujar un rectángulo de selección. Al soltar se abre un formulario donde ponés el nombre. El rectángulo define directamente las esquinas de la región: ya no hay tamaño ni radio, solo arrastrar lo que querés cubrir.

\dark_gray• Si el rectángulo coincide exactamente con una región existente, el formulario abre modo edición (cambiar nombre o eliminar).
\dark_gray• Si es un rectángulo nuevo, el formulario crea una región nueva con esos bounds.
\dark_gray• Enter confirma. Escape o X cierra sin guardar.
\dark_gray• Al editar, Eliminar quita la región.

El overlay naranja muestra cada región con su nombre y dimensiones en chunks.

—————————————————————————————————
\aqua\boldEXPORTACIÓN AUTOMÁTICA\reset
—————————————————————————————————

Cada cambio de regiones actualiza automáticamente tres CSV en la carpeta \yellowconfig\reset del servidor:

\dark_gray• ExplorerManagerOverworldSelection.csv
\dark_gray• ExplorerManagerNetherSelection.csv
\dark_gray• ExplorerManagerEndSelection.csv

Cada fila identifica región MCA y chunk con el formato \whiteregionX;regionZ;chunkX;chunkZ\reset. Es la selección exacta de las regiones registradas, sin margen adicional de 16 chunks. Estos archivos son la fuente que usan herramientas externas como limpieza de mundo; no necesitas ejecutar un comando de exportación.

No edites esos CSV para cambiar regiones: son una vista derivada. Edita las regiones desde el mapa; el servidor reescribirá los CSV correctamente.

—————————————————————————————————
\aqua\boldLÍMITE DE EXPLORACIÓN DE JUGADORES\reset
—————————————————————————————————

La regla \yellowallowPlayerExploration\reset controla si los jugadores pueden salir de regiones registradas.

\dark_gray• En \yellowtrue\reset, la exploración funciona normalmente.
\dark_gray• En \yellowfalse\reset, un jugador que salga de una región permitida vuelve a su última posición válida de esa misma dimensión y recibe un aviso.

La restricción solo funciona si hay al menos una región en la dimensión. Si no hay ninguna, el servidor deja esa dimensión libre para evitar atrapar a alguien sin un punto válido.

Mientras \yellowexplorationManager\reset está activo, la restricción se desactiva temporalmente. Esto permite crear, revisar y pregenerar regiones sin que la administración o jugadores sean devueltos por el límite. Para usar la barrera de exploración, desactiva el manager después de configurar las regiones y pon \yellowallowPlayerExploration\reset en \yellowfalse\reset.

—————————————————————————————————
\red\boldSOLO ADMINISTRACIÓN: PREGENERACIÓN\reset
—————————————————————————————————

La pregeneración recorre cada región completa, una por una, y carga/genera terreno gradualmente. Su objetivo es preparar el área sin producir picos de lag perceptibles.

Durante la pregeneración se añade un margen de \yellow16 chunks por lado\reset alrededor de cada región. Ese margen es solo para generación; no altera la región registrada ni el CSV de selección.

\yellow/exploration pregen start\reset
Inicia la pregeneración o reanuda el progreso guardado. Si el servidor se reinicia, el estado se conserva y puede continuar desde donde quedó.

\yellow/exploration pregen pause\reset
Pausa el trabajo sin perder cursor, región actual, conteo ni velocidad. Úsalo antes de un evento o mantenimiento si quieres retomarlo después.

\yellow/exploration pregen stop\reset
Detiene el trabajo y descarta el progreso de la cola. Conserva la velocidad configurada, pero una nueva ejecución empezará otra vez desde el inicio de las regiones.

\yellow/exploration pregen status\reset
Muestra si está activo, pausado o detenido; región actual, velocidad máxima, estado de rendimiento y promedio MSPT.

\yellow/exploration pregen speed <1-1200>\reset
Define un máximo de chunks por minuto. El valor inicial es 60. Es un techo, no una garantía: el sistema reduce su ritmo si el servidor tiene menos margen.

\aqua\boldPROTECCIONES DE RENDIMIENTO\reset

La pregeneración no empieza a trabajar de inmediato. Primero reúne una muestra por segundo durante cinco minutos. Para generar necesita un historial sano: promedio menor de 20 MSPT, ningún valor por encima de 25 MSPT y una variación total de no más de 6 MSPT.

Con el servidor muy holgado —promedio menor de 12 MSPT— usa hasta el 100 % de la velocidad configurada. Bajo 16 MSPT usa hasta el 50 %; entre 16 y 20, hasta el 25 %. Si las condiciones dejan de ser sanas, se pausa sola hasta recuperar estabilidad.

También evita generar un chunk que esté a ocho chunks o menos de un jugador no espectador de esa dimensión. Así no compite directamente con la zona que alguien está explorando o construyendo.

Cuando termina todas las regiones, queda pausada automáticamente. Puedes revisar Status o volver a Start si cambiaste las regiones y necesitas procesar la nueva selección.

—————————————————————————————————
\aqua\boldFLUJO ADMINISTRATIVO RECOMENDADO\reset
—————————————————————————————————

\dark_gray1. Activa explorationManager y revisa el mapa en la dimensión correcta.
\dark_gray2. Crea las regiones arrastrando con clic derecho sobre el mapa.
\dark_gray3. Verifica que los rectángulos cubran exactamente lo que necesitás.
\dark_gray4. Confirma que los CSV automáticos cambiaron antes de usarlos en una herramienta externa.
\dark_gray5. Define una velocidad de pregeneración prudente y usa Start.
\dark_gray6. Deja que el sistema reúna sus cinco minutos de muestras; no fuerces carga mientras MSPT no sea estable.
\dark_gray7. Al terminar, decide si apagar explorationManager y activar allowPlayerExploration false para convertir las regiones en límite de juego.

Las regiones, CSV y pregeneración tienen propósitos relacionados pero distintos: región selecciona, CSV exporta y pregeneración prepara. No confundas el margen de 16 chunks de generación con la selección que usa el mantenimiento del mundo.
