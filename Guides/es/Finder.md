\gold\boldFINDER: BUSCAR EN ALMACENAMIENTOS\reset

Finder permite localizar y contar ítems dentro de zonas de almacenamiento registradas. Es una herramienta de consulta: no mueve, consume ni modifica ítems. Administración define las zonas; cualquier jugador puede buscar en cualquier zona registrada.

La regla \yellowcommandFinder\reset debe estar activa. Finder guarda las zonas, su dimensión y exclusiones en el mundo.

—————————————————————————————————
\green\boldPARA TODOS: BUSCAR Y CONTAR\reset
—————————————————————————————————

\yellow/find <lugar> <ítem>\reset
Busca el ítem en la zona de almacenamiento indicada (con autocompletado de lugar). También puedes usar \yellownear_me\reset como lugar para buscar en contenedores dentro de un radio de 20 bloques a tu alrededor sin necesidad de una zona registrada. Muestra cada contenedor que lo tiene, con tipo de bloque, coordenadas y cantidad. También dibuja una ruta temporal con partículas y marcadores para llegar a las coincidencias cercanas.

\dark_grayEjemplos: /find MainStorage redstone · /find near_me stone · /find MainStorage cofre de ender

\yellow/count <lugar> <ítem>\reset
Cuenta el total de ítems y stacks del ítem dentro de la zona indicada o en \yellownear_me\reset (radio de 20 bloques). No crea marcadores ni ruta; es la opción rápida cuando solo necesitas saber cuánto hay.

\dark_grayEjemplos: /count MainStorage cohetes de fuegos artificiales · /count near_me redstone

Finder entiende ids técnicos como \whiteminecraft:redstone\reset, nombres en español y nombres normales con espacios. No distingue mayúsculas y normaliza tildes al buscar.

\aqua\boldRESULTADO DE UNA BÚSQUEDA\reset

\yellow/find\reset lista cada coincidencia y después informa cuántos contenedores encontró. La ruta y los marcadores son privados para quien buscó y duran aproximadamente ocho segundos. Si un resultado está muy lejos, puede aparecer listado pero no recibir una línea directa: la guía visual prioriza objetivos cercanos para no saturar el cliente.

\yellow/count\reset informa dos cantidades:

\dark_gray• Ítems: número total de unidades.
\dark_gray• Stacks: número de pilas que contienen ese ítem.

Las shulkers también se revisan por dentro, incluso cuando están dentro de cofres u otras shulkers. Por ejemplo, redstone guardado dentro de una shulker colocada en un cofre sí cuenta para \yellow/find MainStorage redstone\reset y \yellow/count MainStorage redstone\reset.

\aqua\boldCUÁNDO EL RESULTADO SE ACTUALIZA\reset

Finder vuelve a leer la zona completa antes de cada \yellow/find\reset y \yellow/count\reset. No conserva una caché de inventarios entre consultas.

Por eso un ítem que acabas de mover se refleja en la siguiente búsqueda. La consulta puede tardar un poco más que una respuesta basada en caché, especialmente en una zona grande, pero el resultado corresponde al estado que Finder acaba de leer.

—————————————————————————————————
\red\boldSOLO ADMINISTRACIÓN: ZONAS\reset
—————————————————————————————————

\yellow/finder help\reset
Muestra un recordatorio breve de los comandos de administración de Finder.

\yellow/finder scan <coord1> <coord2> <nombre>\reset
Crea una zona nueva o vuelve a escanear una existente. El cubo incluye todos los bloques entre ambas coordenadas y se guarda en la dimensión actual.

\dark_grayEjemplo: /finder scan 0 50 0 127 100 127 MainStorage

El nombre debe usar solo letras (a-z, A-Z) y números (0-9), sin espacios ni símbolos. Una zona admite como máximo 10 000 000 bloques y 256 chunks, equivalente como máximo a una cuadrícula de 16 × 16 chunks. Usa una selección ajustada: escanear una zona enorme carga más chunks y tarda más, aunque se haga gradualmente.

El escaneo revisa un chunk completo por tick y manda progreso al OP que pidió el scan aproximadamente cada dos segundos. Al terminar informa cuántos contenedores encontró.

Finder reconoce cofres, cofres atrapados, barriles, dispensers, droppers y todas las shulkers colocadas. Otros inventarios, como hoppers, no se incluyen actualmente: usa \yellow/finder check\reset si tienes dudas sobre un bloque.

\yellow/finder list\reset
Muestra todas las zonas guardadas, su dimensión y número de contenedores. Cada línea incluye botones de chat:

\dark_gray• ↻: volver a escanearla con sus mismas coordenadas.
\dark_gray• X: eliminarla.

\yellow/finder remove <nombre>\reset
Elimina la zona del registro. No rompe cofres ni cambia bloques; solo deja de usarse en Finder.

—————————————————————————————————
\aqua\boldREVISAR Y EXCLUIR BLOQUES\reset
—————————————————————————————————

\yellow/finder check [coordenadas]\reset
Comprueba si el bloque bajo tus pies —o las coordenadas indicadas— es un tipo de contenedor admitido por Finder. Lo marca brevemente con partículas verdes si entra al scan o rojas si no entra.

\yellow/finder toggle-block [coordenadas]\reset
Excluye o vuelve a incluir ese bloque de todas las zonas registradas que lo contienen. Sin coordenadas usa el bloque bajo tus pies. Sirve para ignorar un cofre concreto sin reducir ni partir toda la zona.

\yellow/finder show_excludes\reset
Lista las posiciones excluidas, agrupadas por zona.

\yellow/finder clean\reset
Elimina todas las entidades \whiteminecraft:block_display\reset cargadas y limpia las rutas y marcadores temporales de Finder. Útil si algún marcador quedó colgado tras un reinicio o descarga de chunks.

Las exclusiones persisten y se respetan al volver a escanear. Si una misma posición pertenece a más de una zona, \yellowtoggle-block\reset cambia su estado en todas ellas; revisa \yellowshow_excludes\reset si trabajas con zonas superpuestas.

—————————————————————————————————
\aqua\boldREESCANEAR Y MANTENER\reset
—————————————————————————————————

Reescanea una zona cuando se agreguen o eliminen cofres, barriles, shulkers colocadas o cualquier estructura de almacenamiento. Las consultas leen los contenedores en ese momento, pero no descubren automáticamente un cofre nuevo que nunca estuvo en el scan inicial.

Los cambios normales de inventario aparecen en la siguiente búsqueda. Para cambios estructurales, usa el botón ↻ de \yellow/finder list\reset o repite \yellow/finder scan\reset con las mismas coordenadas y nombre.

\dark_grayFlujo recomendado:
\dark_gray1. Escanea cada almacén con un nombre claro (solo letras y números).
\dark_gray2. Comprueba las zonas con /finder list.
\dark_gray3. Prueba /find <lugar> y /count <lugar> con un ítem conocido.
\dark_gray4. Excluye cofres que no deban participar.
\dark_gray5. Reescanea después de ampliar o rediseñar el almacenamiento.

Finder funciona mejor con zonas bien delimitadas por almacén, no con una selección que intente cubrir todos los cofres del servidor.
