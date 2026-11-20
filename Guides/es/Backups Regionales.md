\gold\boldBACKUPS REGIONALES\reset

Un backup regional guarda solo regiones elegidas: terreno, POI y entidades de Overworld, Nether y End. Cada región mide 512 × 512 bloques.

—————————————————————————————————
\aqua\boldSELECCIONAR Y CREAR\reset
—————————————————————————————————

\yellow!!rb add\reset
Añade la región donde estás parado.

\yellow!!rb pos1\reset y \yellow!!rb pos2\reset
Marca un rectángulo en la dimensión actual. Se añaden todas las regiones que lo crucen; no selecciona bloques exactos. El máximo total permitido por selección es de \yellow2,500 regiones\reset (50×50, aprox. 25.6k × 25.6k bloques).

\yellow!!rb list\reset
Muestra la selección numerada por dimensión.

\yellow!!rb remove\reset, \yellow!!rb del <número>\reset y \yellow!!rb clear\reset
Quita la región actual, una entrada concreta o toda tu selección.

\yellow!!rb mk-bkp <nombre>\reset
Crea <nombre>.zip con la selección. El servidor guarda el mundo antes de comprimirlo; solo se crea uno a la vez.

\yellow!!rb bkps\reset
Muestra backups regionales con fecha, autor y regiones incluidas.

\yellow!!rb update <nombre>\reset
Actualiza las mismas regiones que ya contenía ese backup. El creador puede actualizar el suyo; administración o whitelist puede actualizar cualquiera.

—————————————————————————————————
\red\boldRESTAURAR Y BORRAR\reset
—————————————————————————————————

\yellow!!rb load-bkp <nombre>\reset y \yellow!!rb confirm\reset
Preparan y confirman restaurar un backup regional. El servidor avisa, espera 5 segundos, se reinicia y carga los archivos con seguridad.

\yellow!!rb del-bkp <nombre>\reset
Borra un backup. El creador puede borrar el suyo; administración o whitelist puede borrar otros.

\yellow!!rb load-md\reset
Lista backups generales disponibles.

\yellow!!rb load-md <nombre>\reset y \yellow!!rb confirm-md\reset
Preparan y confirman importar solo las regiones de tu selección desde un backup general.

—————————————————————————————————
\aqua\boldPERMISOS POR SERVIDOR\reset
—————————————————————————————————

En \yellowSMP\reset, un usuario normal puede seleccionar regiones, crear backups propios, ver la lista y actualizar o borrar únicamente los que creó. No puede restaurar un backup ni importar regiones desde un backup general.

La \yellowwhitelist de reg-bkps\reset concede esas operaciones delicadas sin convertir al jugador en admin: restaurar backups regionales, importar regiones desde backups generales y gestionar backups ajenos. No permite editar la whitelist ni da permisos generales de administración.

Solo administración del SMP gestiona esa whitelist:

\yellow!!rb wl list\reset
Muestra los jugadores actualmente autorizados.

\yellow!!rb wl add <jugador>\reset
Añade a ese jugador a la whitelist de reg-bkps.

\yellow!!rb wl remove <jugador>\reset
Quita a ese jugador de la whitelist.

\yellow!!rb wl clear\reset
Vacía toda la whitelist. Úsalo solo si realmente quieres revocar el acceso de todos los autorizados.

En \yellowMMP, CMP y PMP\reset no hay backups generales: se usan regionales sí o sí. Allí cualquier jugador puede preparar y confirmar una restauración regional; la whitelist no limita esa restauración. Borrar un backup ajeno sigue reservado a su creador, administración o whitelist.

\red\boldRestaurar reemplaza regiones completas. Revisa !!rb list y !!rb bkps antes de confirmar.\reset
