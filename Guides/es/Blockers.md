\gold\boldBLOCKERS\reset

Blockers busca dentro de una zona los bloques que pueden detener, interferir o volver inseguro un mecanismo de pistones. El análisis no rompe, mueve ni reemplaza bloques: solo registra posiciones para poder revisarlas y señalarlas.

Para que exista el sistema, administración debe activar \yellowcommandBlockers\reset con Carpet. Una vez activo, jugadores y OP comparten la misma interfaz de consulta, pero no los mismos controles.

—————————————————————————————————
\aqua\boldQUÉ CUENTA COMO BLOQUEADOR\reset
—————————————————————————————————

Un resultado aparece por una de estas dos razones:

\dark_gray• El bloque está en la lista configurada de bloqueadores.
\dark_gray• El bloque tiene la propiedad de estar waterlogged, es decir, contiene agua.

La lista inicial incluye obsidiana, obsidiana llorosa, cofre de Ender, bedrock, deepslate reforzada, marco de portal del End y bloque de portal del End. Administración puede ajustarla; el agua embebida se detecta siempre porque también puede afectar mecanismos.

Los resultados guardan el tipo de bloque, sus coordenadas y el motivo. Un análisis pertenece a la dimensión donde fue pedido: Overworld, Nether y End se revisan por separado.

—————————————————————————————————
\green\boldPARA JUGADORES\reset
—————————————————————————————————

\yellow/blockers\reset
Abre la lista de análisis existentes. Selecciona uno para ver sus bloqueadores, cuántos encontró y si todavía está trabajando. Todos pueden consultar resultados, incluso si otra persona pidió el análisis.

\yellow/blockers <coord1> <coord2> <nombre>\reset
Pide un análisis del cubo comprendido entre las dos coordenadas, en la dimensión actual.

\dark_grayEjemplo: /blockers 100 60 -80 180 100 0 granja_norte

El nombre identifica el análisis, por lo que debe ser único y solo puede llevar minúsculas, números, guion bajo y guion medio. El sistema rechaza nombres repetidos: no reutilices uno de un scan anterior sin pedir a un OP que borre ese registro.

Cada análisis puede abarcar como máximo \yellow200 000 000 bloques\reset. Parece alto, pero sigue siendo un trabajo grande: el servidor carga y lee los chunks necesarios poco a poco. No pidas una caja enorme “por si acaso”; delimita la máquina o construcción que realmente necesitas revisar.

Para mantener el servidor estable, cada jugador puede tener \yellowun análisis pendiente\reset a la vez y el servidor admite \yellowcuatro pendientes\reset en total. Cuando un scan termina, puedes pedir otro. Mientras avanza, quien lo solicitó recibe progreso en el chat; al terminar, todos reciben un aviso.

\aqua\boldLEER UN ANÁLISIS\reset

Dentro de un análisis, cada fila muestra:

\dark_gray• \whiteBloque\reset: el tipo de bloque encontrado.
\dark_gray• \whiteCoordenadas\reset: su posición exacta.
\dark_gray• \whiteMotivo\reset: si viene de la lista de bloqueadores o de estar waterlogged.

Puedes hacer clic en una o varias filas. Los bloques elegidos aparecen en el mundo como cajas moradas semitransparentes, visibles incluso a través de paredes. Es una guía visual personal: no se comparte, no da permisos adicionales y no modifica el bloque.

\yellowSeleccionar todo\reset marca todos los resultados de ese análisis. \yellowLimpiar selección\reset apaga las cajas moradas. También se limpian si el resultado deja de existir en el registro, por ejemplo después de romper el bloque o borrar el análisis.

La lista tiene rueda de ratón y barra arrastrable cuando hay más resultados de los que caben en pantalla. Usa el botón de volver para regresar a la lista de scans o la X para cerrar la interfaz.

—————————————————————————————————
\red\boldSOLO ADMINISTRACIÓN\reset
—————————————————————————————————

Los OP administran qué cuenta como bloqueador y qué análisis permanecen guardados. Los jugadores pueden pedir y leer scans, pero no cambiar estos datos compartidos.

\yellow/blockers list\reset
Muestra la lista actual de tipos de bloque que Blockers considera configurados. Cualquier jugador puede verla; sirve para saber qué buscará el próximo scan.

\yellow/blockers list add <bloque>\reset — \redSOLO OP\reset
Añade un tipo de bloque a la lista. Acepta ids completos, como \yellowminecraft:slime_block\reset, o nombres vanilla cortos cuando correspondan. Los análisis futuros sí tendrán en cuenta el bloque; un análisis ya terminado no se recalcula automáticamente.

\yellow/blockers list remove <bloque>\reset — \redSOLO OP\reset
Quita un tipo de bloque de la lista. No elimina bloques del mundo ni borra resultados ya guardados; solo cambia los análisis que se hagan después.

\aqua\boldBORRAR UN ANÁLISIS\reset

En la lista de scans, los OP ven una X a la derecha de cada análisis. Deben mantener \yellowShift\reset mientras hacen clic para activarla. Así se evita borrar por accidente.

Borrar un scan elimina su registro y sus resultados; no modifica ningún bloque del mundo. Si el análisis aún estaba pendiente, también cancela su trabajo en la cola. Todos reciben un mensaje indicando que fue eliminado.

—————————————————————————————————
\aqua\boldCUÁNDO VOLVER A ANALIZAR\reset
—————————————————————————————————

Los resultados se actualizan si un jugador rompe uno de los bloques encontrados: esa entrada desaparece del análisis. Sin embargo, colocar nuevos bloques, cambiar agua embebida o modificar gran parte de la zona no completa el registro automáticamente. Para una revisión fiel después de cambios importantes, crea un scan nuevo con otro nombre o pide a un OP eliminar el anterior y reutilizar su nombre.

\dark_grayRecomendación: usa un nombre por máquina y revisión, por ejemplo granja_hierro_v1 o storage_este_2026. Así es claro qué construcción representa cada resultado.

—————————————————————————————————
\red\boldBUENAS PRÁCTICAS\reset
—————————————————————————————————

Selecciona el menor volumen útil, espera a que termine antes de pedir otra revisión y no uses Blockers como una búsqueda global del mundo. Si no sabes qué bloque está frenando una máquina, revisa primero una sección concreta y usa las cajas moradas para llegar a los candidatos antes de modificar nada.
