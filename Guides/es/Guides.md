\gold\boldGUÍAS DEL SERVIDOR\reset

Las guías son la biblioteca de ayuda visible dentro de Minecraft. Sirven para que jugadores y administradores consulten procedimientos del servidor sin depender de Discord, de archivos locales ni de otra persona conectada.

El servidor es la fuente de verdad. Las guías viven como archivos en subdirectorios por idioma: \yellowworld/data/aeternum_guides/es/\reset y \yellowworld/data/aeternum_guides/en/\reset. Se envían al cliente al abrir la biblioteca. Para usar la interfaz, cliente y servidor necesitan Aeternum Carpet.

Para habilitarla, administración activa la regla \yellowcommandGuide\reset.

—————————————————————————————————
\green\boldPARA TODOS: LEER GUÍAS\reset
—————————————————————————————————

\yellow/guide\reset
Abre tu biblioteca personal de guías en español. No modifica nada ni avisa a otros jugadores.

Los botones \yellow[ES]\reset y \yellow[EN]\reset en la esquina superior cambian entre las guías en español y en inglés. Cada idioma tiene su propio conjunto independiente de guías, orden y archivos. El tooltip de cada botón está en su propio idioma.

La columna izquierda contiene los títulos. Haz clic en uno para leerlo a la derecha. Si hay demasiados títulos, usa la rueda sobre esa columna; los títulos largos se recortan visualmente para no salir del panel, pero su contenido no se pierde.

El texto de una guía puede ser más largo que el área visible. Usa la rueda sobre el texto o arrastra la barra vertical de la derecha. Los saltos de línea se respetan: una línea vacía en el archivo crea separación en el lector.

Solo los OP ven los botones \yellowEditar\reset y \yellowRefrescar\reset. Un jugador normal solo puede consultar, cambiar de idioma y cerrar la biblioteca.

—————————————————————————————————
\red\boldSOLO ADMINISTRACIÓN: EDITAR\reset
—————————————————————————————————

Selecciona una guía y pulsa \yellowEditar\reset. El botón pasa a \yellowGuías\reset para volver claramente al lector sin cerrar todo el panel. Escape también vuelve del editor al lector; desde el lector cierra la biblioteca.

Las ediciones se guardan en el subdirectorio del idioma activo. Si estás viendo guías en español, los cambios van a \yellowes/\reset. Cambiá de idioma con los botones superiores para editar el otro conjunto.

\aqua\boldCONTENIDO Y GUARDADO AUTOMÁTICO\reset

Escribe directamente en el área grande del editor. No hay botón Guardar: unos instantes después de dejar de escribir, el estado cambia de \yellowGuardando...\reset a \greenGuardado\reset y el servidor escribe el archivo.

No cierres el juego justo mientras aparezca \yellowGuardando...\reset. Espera a que muestre \greenGuardado\reset para confirmar que el último cambio llegó al servidor.

Cada guía puede contener hasta 100 000 caracteres. El editor conserva los saltos de línea y permite desplazarse por textos largos.

\aqua\boldCREAR\reset

El botón \yellow+\reset crea una guía nueva en el idioma actual. El servidor parte de \whiteGuia nueva\reset; si ya existe, crea \whiteGuia nueva 2\reset, \whiteGuia nueva 3\reset y así sucesivamente. Luego escribe el título y contenido finales.

\aqua\boldRENOMBRAR\reset

Arriba del contenido está el campo de título. El botón ✓ permanece apagado mientras el título sea el mismo. Al escribir un título distinto y válido se enciende; púlsalo para confirmar el cambio.

El título es también el nombre del archivo. Debe ser único y puede tener entre 1 y 64 caracteres: letras sin acento, números, espacios, \white_\reset y \white-\reset. No uses /, \#, tildes, signos de puntuación u otros caracteres especiales.

Renombrar cambia el archivo \white<Título>.md\reset. Si ya existe una guía con el título elegido, el cambio se rechaza para no sobrescribirla.

\aqua\boldORDENAR\reset

En el editor, cada fila de la lista de guías muestra dos flechas: ▲ para subir una posición y ▼ para bajar. El orden se guarda en \yellow.aeternum_guide_order\reset dentro de la carpeta del idioma correspondiente.

\aqua\boldELIMINAR\reset

El botón X borra la guía seleccionada y su archivo. Debes mantener \yellowShift\reset para activarlo. No hay papelera ni confirmación adicional: antes de eliminar una guía importante, cópiala o verifica que esté en control de versiones.

—————————————————————————————————
\aqua\boldFORMATO DEL TEXTO\reset
—————————————————————————————————

Aunque los archivos usan extensión \white.md\reset, el lector no renderiza Markdown o HTML. Por ejemplo, \white# título\reset, \white**negrita**\reset y enlaces Markdown se mostrarán como texto normal.

Usa el mismo formato de colores y estilos del banner de bienvenida. Escribe una barra invertida seguida del nombre del color o estilo justo antes del texto que quieres afectar. Para volver al estilo normal, escribe una barra invertida seguida de \whitereset\reset.

\aqua\boldCOLORES\reset

\whiteblack — negro · dark_blue — azul oscuro · dark_green — verde oscuro
dark_aqua — aqua oscuro · dark_red — rojo oscuro · dark_purple — púrpura oscuro
gold — dorado · gray — gris · dark_gray — gris oscuro · blue — azul
green — verde · aqua — aqua · red — rojo · light_purple — lila
yellow — amarillo · white — blanco

\aqua\boldESTILOS\reset

\whitebold\reset — negrita
\whiteitalic\reset — cursiva
\whiteunderline\reset — subrayado
\whitestrikethrough\reset — tachado
\whiteobfuscated\reset — texto ofuscado
\whitereset\reset — vuelve a color y estilo normales

\dark_grayEjemplo conceptual: escribe barra invertida seguida de aqua y bold antes de un título; escribe barra invertida seguida de reset al terminar. Para un aviso, escribe barra invertida seguida de red y bold antes de "Atención", y reset después.

El botón ? del editor muestra una chuleta con los códigos disponibles. Úsalo si no recuerdas la sintaxis mientras escribes.

—————————————————————————————————
\red\boldRECARGAR ARCHIVOS DEL SERVIDOR\reset
—————————————————————————————————

\yellowRefrescar\reset — \redSOLO OP\reset
Vuelve a leer la carpeta de guías del idioma actual. Detecta archivos añadidos, editados, renombrados o eliminados fuera del juego y sincroniza la biblioteca de jugadores conectados que estén viendo ese mismo idioma.

Úsalo después de copiar una guía nueva, actualizar archivos desde un repositorio o modificar texto con un editor externo. No hace falta reiniciar el servidor.

Al recargar, solo se consideran archivos \white.md\reset cuyo nombre sea un título válido. Un archivo con caracteres no permitidos en el nombre se ignora hasta que se renombre correctamente.

Si editas un archivo externo mientras alguien tiene su guía abierta en el editor con cambios pendientes, ese cliente conserva temporalmente su edición para no pisarla. Espera a que guarde o pide a la persona salir del editor antes de una recarga importante.

—————————————————————————————————
\aqua\boldFLUJO RECOMENDADO\reset
—————————————————————————————————

\dark_gray1. Crea o selecciona una guía desde /guide.
\dark_gray2. Escribe el título y contenido; revisa que aparezca Guardado.
\dark_gray3. Usa ? para comprobar colores y estilos.
\dark_gray4. Vuelve a Guías, léela como jugador y verifica saltos de línea y desplazamiento.
\dark_gray5. Ordena la guía con ▲ y ▼ en la lista si hace falta.
\dark_gray6. Si el cambio vino de archivos externos, pulsa Refrescar.

Mantén los títulos cortos y claros. La biblioteca funciona mejor cuando cada guía responde a una necesidad concreta y Comandos.md enlaza a la guía detallada correspondiente.
