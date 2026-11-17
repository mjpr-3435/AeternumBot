\gold\boldLIMPIEZA DEL MUNDO\reset

La limpieza elimina chunks fuera de las áreas de exploración permitidas. Los CSV exportados por AeternumCarpet son la fuente de verdad: los chunks seleccionados se conservan y el resto puede borrarse.

\red\boldSOLO OPERADOR CONFIGURADO\reset

Esta herramienta está restringida por configuración: solo el jugador definido en \yellowWorldTrimmer.Operator\reset (en \yellowconfig.yml\reset / \yellow/config\reset) puede preparar o confirmar una poda. No basta con ser administrador.

\dark_grayLa razón es simple: es una operación destructiva sin papelera, así que se reserva al operador designado que mantiene el flujo de exploración, CSV y limpieza.

\yellow!!trim\reset
Prepara una limpieza. Comprueba los CSV de Overworld, Nether y End y muestra cuántos chunks se conservarán. Preparar no borra nada.

\yellow!!trim confirm\reset
Confirma la limpieza preparada. Debe confirmarla el mismo operador configurado que la preparó.

—————————————————————————————————
\red\boldANTES DE CONFIRMAR\reset
—————————————————————————————————

1. Revisar áreas de exploración y su exportación en AeternumCarpet.
2. Hacer un backup general independiente.
3. Ejecutar !!trim y verificar los números mostrados.
4. Confirmar solo si esa selección representa exactamente lo que debe sobrevivir.

\dark_grayNo se añade radio ni margen oculto: se preserva exactamente lo indicado por los CSV. Si hace falta más terreno, se amplían las áreas antes de preparar.

Si una dimensión tiene chunks almacenados pero su CSV de preservación está vacío, se cancela por seguridad en vez de vaciarla.

Durante la operación el servidor está detenido. Se eliminan datos de región, POI y entidades fuera de la selección, y el servidor vuelve a iniciar incluso si ocurrió un error.

\red\boldLa herramienta no crea un backup propio.\reset En el primer uso puede descargar y verificar MCA Selector; el resultado queda en la consola del proceso.
