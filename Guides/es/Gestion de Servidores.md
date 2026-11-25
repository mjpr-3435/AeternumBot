\gold\boldGESTIÓN DE SERVIDORES\reset

Estos comandos controlan procesos administrados por AeternumBot: servidores y redes.

—————————————————————————————————
\aqua\boldPARA TODOS\reset
—————————————————————————————————

\yellow!!pm help\reset
Muestra la ayuda disponible.

\yellow!!status\reset
Muestra CPU, RAM, disco y el estado de cada proceso. Pasa el cursor por los indicadores para ver detalles.

\yellow!!start <proceso>\reset
Inicia un proceso apagado.

\dark_grayEjemplos: !!start SMP, !!start MMP, !!start CMP

Si el proceso ya estaba abierto, no se inicia una segunda vez. Puedes consultar estado e iniciar uno detenido, pero no detener ni reiniciar procesos ajenos.

—————————————————————————————————
\red\boldSOLO ADMINISTRACIÓN\reset
—————————————————————————————————

\yellow!!stop [proceso]\reset
Detiene el proceso indicado. Sin argumento, detiene el servidor actual.

\yellow!!restart [proceso]\reset
Reinicia el proceso indicado. Sin argumento, reinicia el servidor actual.

\yellow!!mdreload [proceso]\reset
Recarga los mdplugins. Sin argumento, los del servidor actual. Aplica comandos y automatizaciones actualizados sin reiniciar Minecraft cuando el plugin lo permite.

\yellow!!adreload\reset
Recarga los mdaddons de AeternumBot. Puede volver a sincronizar plugins y guías administrados.

\red\boldAntes de detener o reiniciar, avisa y revisa !!status. Un reinicio corta conexiones y puede cancelar backups, actualizaciones o limpiezas en curso.\reset
