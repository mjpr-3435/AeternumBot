\gold\boldMATERIALES: LISTAS DE RECOLECCIÓN DE PROYECTOS\reset

El sistema de materiales controla los ítems que necesita un proyecto y cuántos faltan todavía. Compara las cantidades objetivo contra lo que hay almacenado en una única zona de almacenamiento y lo que lleva cada jugador.

Administración activa \yellowcommandProjects\reset para habilitar \yellow/materials\reset y \yellow/projects\reset. La interfaz requiere el cliente Aeternum Carpet.

—————————————————————————————————
\aqua\boldCÓMO SE CREAN LAS LISTAS\reset
—————————————————————————————————

Cada lista es un archivo CSV dentro de \yellowworld/data/aeternum_materials/\reset. El nombre del archivo se convierte en el título de la lista. Columnas:

\dark_gray• \whiteItem\reset: nombre visible del ítem (por ejemplo "White Wool").
\dark_gray• \whiteTotal\reset: cuántos de ese ítem necesita el proyecto.
\dark_gray• \whiteMissing\reset y \whiteAvailable\reset: informativas. El available real proviene del escaneo del almacenamiento, no del CSV.

\yellow/materials\reset — \greenPARA TODOS\reset
Abre el panel de listas. Elegí una lista para abrir su pantalla de detalle con las columnas Item, Total, Falta y Claim.

—————————————————————————————————
\aqua\boldALMACENAMIENTO: UNA ZONA POR LISTA\reset
—————————————————————————————————

Cada lista tiene una única zona de almacenamiento. El servidor la escanea cada segundo y actualiza cuántos ítems hay disponibles.

\yellow/materials storage add <lista> <coord1> <coord2>\reset — \redSOLO OP\reset
Asigna la zona de almacenamiento de una lista. Si la lista ya tiene una, el comando se rechaza: primero hay que eliminar la existente antes de asignar otra.

\yellow/materials storage list\reset — \redSOLO OP\reset
Muestra las zonas de almacenamiento asignadas con una X clicable para eliminar una.

\yellow/materials storage del <lista> <índice>\reset — \redSOLO OP\reset
Elimina la zona de almacenamiento indicada.

—————————————————————————————————
\aqua\boldCLAIMS\reset
—————————————————————————————————

Cada jugador puede claimear un ítem de una lista con su botón Claim para responsabilizarse de farmearlo. La pantalla de detalle muestra quién claimó cada ítem; solo el claimant puede desclaimearlo.

—————————————————————————————————
\aqua\boldORDEN DE LA LISTA\reset
—————————————————————————————————

La pantalla de detalle muestra dos grupos:

\dark_gray1. Primero los ítems faltantes (available por debajo del objetivo), ordenados por total de mayor a menor.
\dark_gray2. Después los ítems ya completados (available igual o superior al objetivo), también ordenados por total de mayor a menor.

—————————————————————————————————
\aqua\boldOVERLAY EN EL HUD\reset
—————————————————————————————————

Mientras jugás, el overlay de la derecha muestra tus ítems claimados que todavía faltan, ordenados por total de mayor a menor. El conteo lo calcula el servidor y considera tanto la zona de almacenamiento como lo que llevás en tu inventario, incluido el contenido de shulkers y shulkers dentro de shulkers.

Esto permite recolectar sin tener que depositar constantemente: el faltante baja a medida que cargás los ítems, y cuando almacén más inventario cubren el objetivo, el ítem desaparece del overlay. El overlay es personal, se refresca desde el servidor y se limpia solo al cambiar de mundo o reconectarte.

—————————————————————————————————
\aqua\boldFORMATO DE CANTIDADES\reset
—————————————————————————————————

Las cantidades se muestran en unidades progresivas:

\dark_gray• Ítems sueltos: el número directamente.
\dark_gray• Stacks: \yellow64 x N + Y\reset.
\dark_gray• \yellowSB\reset (Shulker Box): por encima de 1.728 ítems, contados en shulkers de 1.728.
\dark_gray• \yellowSDC\reset (Shulker Double Chest): por encima de 93.312 ítems, contados en cofres dobles de shulker boxes (54 shulkers cada uno).

\dark_grayEjemplo: 93.312 ítems = 1 SDC = 54 shulkers.
