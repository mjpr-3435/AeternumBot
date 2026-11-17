\gold\boldBACKUPS GENERALES\reset

Un backup general copia el servidor completo: mundo, configuraciones y archivos del proceso. Es distinto a un backup regional, que solo guarda regiones elegidas.

—————————————————————————————————
\aqua\boldPARA TODOS\reset
—————————————————————————————————

\yellow!!bk\reset o \yellow!!bk help\reset
Muestra la ayuda.

\yellow!!bkps\reset
Lista los backups disponibles con fecha, autor y comentario si existe.

\yellow!!mk-bkp [comentario]\reset
Crea un backup completo. El servidor guarda el mundo antes de copiarlo, avisa a los jugadores y solo permite una copia a la vez.

\dark_grayEjemplo: !!mk-bkp antes_de_actualizar_el_spawn

—————————————————————————————————
\aqua\boldCÓMO SE GUARDAN\reset
—————————————————————————————————

La configuración actual conserva \yellow3 backups manuales\reset: los slots SMP 1, SMP 2 y SMP 3. Cada backup manual nuevo ocupa el slot más reciente y los anteriores se desplazan.

Cuando esos tres slots están llenos, el sistema rota uno antiguo para hacer espacio. Si existe algún backup creado por un administrador, protege siempre al menos el backup administrativo más reciente durante esa rotación.

\aquaEjemplo:\reset hay tres backups manuales. El más antiguo fue creado por un admin; los otros dos son de usuarios. Al crear uno nuevo, normalmente se borraría el más antiguo, pero en este caso se conserva el administrativo y se descarta el backup de usuario más antiguo.

\dark_grayLos nombres SMP 1, 2 y 3 se reordenan tras cada copia. Para identificar un backup, mira fecha y autor con !!bkps, no solo su número. Siempre siguen existiendo tres manuales; el cuarto slot es exclusivamente el automático.

—————————————————————————————————
\aqua\boldBACKUP AUTOMÁTICO\reset
—————————————————————————————————

El backup automático usa un slot separado: \yellowSMP 4\reset. Si no existe uno válido, se crea al iniciar el sistema; luego se reemplaza aproximadamente cada 24 horas.

\dark_graySolo hay una copia automática. La siguiente ejecución sustituye SMP 4; no ocupa ni rota los tres slots manuales.

También guarda el mundo y avisa mientras trabaja. Si un backup manual está en curso, espera antes de intentarlo otra vez.

\red\boldEl automático ayuda ante accidentes recientes, pero crea uno manual antes de una actualización, restauración o limpieza.\reset

—————————————————————————————————
\red\boldSOLO ADMINISTRACIÓN\reset
—————————————————————————————————

\yellow!!load-bkp <nombre>\reset
Prepara cargar un backup completo.

\yellow!!bk confirm\reset
Confirma la carga. El servidor avisa a todos, espera 5 segundos, se detiene, restaura los archivos y vuelve a iniciar.

\yellow!!del-bkp <nombre>\reset
Elimina un backup completo de forma definitiva.

\dark_grayRestaurar reemplaza el estado actual del servidor, no solo el mundo. Revisa nombre, fecha, autor y comentario con !!bkps antes de confirmar.
