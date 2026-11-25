\gold\boldPAQUETES DE ACCIONES\reset

Actions permite guardar secuencias de comandos del servidor bajo un nombre y ejecutarlas desde un panel o escribiendo \yellow!!Nombre del paquete\reset. Sirve para automatizaciones repetibles: preparar un evento, controlar bots, activar mecanismos o lanzar varios comandos en un orden definido.

La regla \yellowcommandActions\reset debe estar activa. Los paquetes se guardan en el mundo, en \yellowworld/data/aeternum_command_packs.json\reset, y el servidor es la fuente de verdad. Para usar el panel se necesita Aeternum Carpet tanto en cliente como en servidor.

\red\boldIMPORTANTE\reset
Cada comando de un paquete se ejecuta como el servidor. No usa los permisos del jugador que pulsó Ejecutar. Por eso cualquier paquete disponible debe ser seguro para que lo ejecute cualquier jugador.

—————————————————————————————————
\green\boldPARA TODOS: CONSULTAR Y EJECUTAR\reset
—————————————————————————————————

\yellow/actions\reset
Abre el catálogo de paquetes. La lista se ordena alfabéticamente y el campo Filtrar por título permite escribir una parte del nombre para mostrar solo coincidencias.

Haz clic sobre una fila para abrir el paquete. Sin OP se abre en modo de solo lectura: puedes revisar nombre, descripción, tipo de cada paso y su contenido, pero no cambiar nada.

\yellow▶ Ejecutar\reset
El botón ▶ a la derecha de un paquete lo inicia. También existe el botón \yellowEjecutar\reset dentro de la vista de un paquete. Si ese mismo paquete ya se está ejecutando, el servidor lo rechaza para evitar duplicarlo.

\yellow!!<nombre completo del paquete>\reset
Ejecuta un paquete directamente desde el chat. El nombre debe ser completo, pero no distingue mayúsculas: \yellow!!bedbot on\reset y \yellowBedBot ON\reset encuentran el mismo paquete. Si no existe, o ya está corriendo, el ejecutor recibe el aviso correspondiente.

\aqua\boldQUÉ SE VE AL EJECUTAR\reset

Todos los jugadores conectados reciben los avisos de Actions:

\dark_gray• Al iniciar: el nombre del paquete que se está ejecutando.
\dark_gray• Por cada comando: ✓ si el servidor lo aceptó o ✕ si falló, seguido del comando.
\dark_gray• Al final: \greenAcción terminada.\reset

El símbolo ✓ confirma que el comando devolvió éxito al servidor; no sustituye revisar el resultado en el mundo cuando una orden depende de entidades, condiciones, permisos o datos externos. Si un paso falla, Actions lo marca con ✕ y continúa con el siguiente paso. Un fallo no cancela automáticamente todo el paquete.

\aqua\boldESPERAS Y RITMO\reset

Actions procesa el trabajo gradualmente: no bloquea el servidor esperando. Una espera se cuenta en segundos y deja pasar ese tiempo antes de continuar. Los comandos se encolan en el ciclo normal del servidor, lo que evita bloqueos con comandos de Carpet como \yellow/player ... spawn\reset.

Un paquete puede ejecutarse mientras otro paquete distinto está activo. Evita crear paquetes que compitan por el mismo bot, entidad, zona o mecanismo: Actions mantiene el orden dentro de cada paquete, no resuelve conflictos entre paquetes distintos.

—————————————————————————————————
\red\boldSOLO ADMINISTRACIÓN: CREAR Y EDITAR\reset
—————————————————————————————————

Los OP ven \yellow+ Nuevo paquete\reset en el catálogo y pueden editar cualquier paquete. La edición no se publica hasta pulsar \yellowGuardar\reset; salir con Escape o cerrar el editor descarta los cambios no guardados de esa edición.

\aqua\boldCREAR UN PAQUETE\reset

1. Abre \yellow/actions\reset y pulsa \yellow+ Nuevo paquete\reset.
2. Escribe un nombre claro y una descripción opcional.
3. Pulsa \yellow+ Nueva línea\reset para crear el primer paso.
4. Añade los comandos y esperas en el orden requerido.
5. Pulsa \yellowGuardar\reset.
6. Ejecútalo una vez y revisa el feedback antes de anunciarlo a jugadores.

El nombre es obligatorio, admite hasta 80 caracteres y debe ser único ignorando mayúsculas. No puedes tener \whiteBed\reset y \whitebed\reset como paquetes separados. La descripción admite hasta 240 caracteres y solo documenta el paquete: no se ejecuta.

\aqua\boldAÑADIR Y EDITAR PASOS\reset

\yellow+ Nueva línea\reset añade un paso de comando al final. Cada paquete permite hasta 128 pasos.

Cada línea tiene un selector:

\dark_gray• \yellowCMD\reset: la línea es un comando de servidor.
\dark_gray• \yellowESPERA\reset: la línea es una duración en segundos.

Pulsa CMD o ESPERA para cambiar el tipo de la línea. Al cambiar a espera, el valor inicial es 1 segundo; al volver a comando, el valor inicial es \whitesay \reset. Escribe el valor final antes de guardar.

Un comando admite hasta 2048 caracteres. Puedes escribirlo con / inicial o sin ella: Actions quita una / inicial antes de enviarlo al servidor. No pegues varias órdenes separadas por saltos de línea en un solo CMD; usa una línea por orden para que el feedback y las esperas mantengan sentido.

Una espera admite de 0 a 3600 segundos. \yellow0\reset no añade una pausa útil, pero es válido. Para esperar más de una hora, usa varias líneas de espera y deja claro el motivo en la descripción.

Cuando hay más de seis pasos, usa la rueda sobre la lista o arrastra su barra para llegar a los demás. Antes de desplazarte, el editor conserva el valor de la línea que estabas editando.

\aqua\boldGUARDAR Y VALIDAR\reset

\yellowGuardar\reset se activa solo cuando hay cambios pendientes. Al pulsarlo, el servidor valida todos los paquetes: nombres únicos, campos obligatorios, límite de texto, tipo de cada paso y segundos válidos.

Si se rechaza, revisa el mensaje \redDatos rechazados\reset o el aviso del editor. No se guarda una versión parcial: corrige el problema y vuelve a pulsar Guardar.

Al guardar, el catálogo se ordena alfabéticamente y todos los jugadores conectados reciben la versión actualizada. Esto permite que puedan ejecutar el paquete nuevo sin reconectarse.

\aqua\boldELIMINAR\reset

En la lista principal, la X de cada paquete requiere mantener \yellowShift\reset. En el editor, el botón \yellowEliminar\reset también requiere Shift. La eliminación borra el paquete guardado y no tiene papelera ni confirmación adicional.

No elimines un paquete que esté siendo usado o documentado sin avisar. Si solo quieres retirarlo temporalmente, cambia su nombre o descripción de forma explícita y guarda; recuerda que sigue siendo ejecutable mientras permanezca en el catálogo.

—————————————————————————————————
\aqua\boldDISEÑAR PAQUETES SEGUROS\reset
—————————————————————————————————

\dark_gray• Usa nombres que expliquen el efecto: abrir_evento, apagar_bot_miner o reiniciar_tnt_duper.
\dark_gray• Describe a quién afecta y qué condición debe cumplirse antes de ejecutarlo.
\dark_gray• Empieza con una orden inocua de aviso si el paquete hace algo importante.
\dark_gray• Separa acciones que necesiten tiempo real con ESPERA, no con comandos repetidos.
\dark_gray• Prueba cada paquete en un entorno seguro o con una versión pequeña antes de dejarlo visible para todos.
\dark_gray• Evita órdenes destructivas o irreversibles en un paquete público. Si son inevitables, no lo dejes disponible para ejecutar por jugadores normales.

Actions está pensado para paquetes públicos y revisados. Como todos pueden lanzarlos, la seguridad no está en quién hace clic: está en qué comandos decidió guardar administración.
