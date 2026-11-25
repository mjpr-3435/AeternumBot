\gold\boldACTUALIZADOR DE REGIONES\reset

El actualizador existe en los servidores creativos, no en SMP Survival. Copia regiones reales del SMP hacia CMP, MMP o PMP para trabajar con el terreno, construcciones y contexto original sin tocar Survival ni usar creativo allí.

—————————————————————————————————
\aqua\boldSELECCIONAR\reset
—————————————————————————————————

\yellow!!ru add\reset
Marca la región actual para copiarla desde SMP al servidor creativo actual.

\yellow!!ru pos1\reset y \yellow!!ru pos2\reset
Marcan dos esquinas en la misma dimensión para añadir todas las regiones del rectángulo a la lista de copia desde SMP.

\yellow!!rm add\reset
Marca la región actual para eliminarla del servidor creativo actual.

\yellow!!rm pos1\reset y \yellow!!rm pos2\reset
Marcan dos esquinas en la misma dimensión para añadir todas las regiones del rectángulo a la lista de borrado.

\yellow!!ru list\reset
Muestra la lista: \greenru\reset significa copiar desde SMP y \redrm\reset significa eliminar del destino.

\yellow!!ru clear\reset
Vacía ambas listas y limpia cualquier esquina \yellowpos1\reset / \yellowpos2\reset pendiente.

\dark_grayCada región mide 512 × 512 bloques. Incluye una región completa de Overworld, Nether o End según dónde estés; no es una selección fina. El máximo por lista es de \yellow2,500 regiones\reset (aprox. 25.6k × 25.6k bloques).

—————————————————————————————————
\aqua\boldACTUALIZAR EL SERVIDOR CREATIVO\reset
—————————————————————————————————

\yellow!!ru update\reset
Aplica la lista actual. Está disponible para quienes puedan usar el servidor creativo; no requiere permisos de administrador.

El sistema avisa a todos, espera 5 segundos, guarda SMP si está encendido, detiene el servidor destino, aplica cambios y lo vuelve a iniciar.

Al copiar, se trasladan juntos terreno, entidades y datos de POI. El SMP solo es origen: este comando nunca modifica la región original del SMP.

\red\boldNo hay confirmación adicional. Usa !!ru list justo antes de actualizar.\reset Los jugadores del destino serán expulsados durante el reinicio.

\red\boldEliminar con !!rm add o !!rm pos1/pos2 no tiene papelera.\reset Si el destino contiene trabajo que quieras conservar, crea antes un backup regional.
