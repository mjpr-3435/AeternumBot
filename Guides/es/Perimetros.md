\gold\boldPERÍMETROS Y WORLD EATER\reset

El sistema de perímetros permite registrar áreas de World Eater, vigilar el avance de la limpieza hasta una altura Y objetivo, recibir alertas de estancamiento en Discord y desplegar una grilla de bots espectadores para mantener chunks cargados.

Para que exista el sistema, administración debe activar \yellowcommandPerimeters\reset con Carpet. Además, las alertas hacia Discord dependen del plugin \yellowworld-eater.py\reset y la configuración \yellowWorldEater\reset en \yellowAeternumBot\reset.

—————————————————————————————————
\aqua\boldCOMANDOS E INTERFAZ\reset
—————————————————————————————————

\yellow/perimeter\reset — \redSOLO OP\reset
Abre la pantalla visual (\yellowPerimetersScreen\reset) para consultar perímetros registrados, ver su progreso actual, ajustar la Y objetivo o el timeout de estancamiento y controlar la grilla de bots. Requiere el cliente Aeternum Carpet.

\yellow/perimeter add <nombre> <x1> <z1> <x2> <z2>\reset — \redSOLO OP\reset
Registra un nuevo perímetro rectangular entre ambas coordenadas X/Z.

\dark_grayEjemplo: /perimeter add main_we -500 -500 500 500

El nombre solo admite minúsculas, números, guion bajo y guion medio (máx. 48 caracteres), y el área máxima permitida es de \yellow200 000 000 bloques\reset.

—————————————————————————————————
\aqua\boldALERTAS Y MONITOREO\reset
—————————————————————————————————

\dark_gray• \whiteY objetivo:\reset altura mínima que debe alcanzar la excavación antes de notificar que el perímetro quedó limpio.
\dark_gray• \whiteTimeout de estancamiento:\reset segundos sin progreso antes de disparar una alerta de atasco.
\dark_gray• \whiteAvisos en Discord:\reset \yellowAeternumBot\reset envía las alertas al canal configurado en \yellowWorldEater.Channel ID\reset y por mensaje directo si \yellowWorldEater.Allow DM\reset está activado en \yellow/config\reset.

—————————————————————————————————
\aqua\boldGRILLA DE BOTS ESPECTADORES\reset
—————————————————————————————————

Desde la pantalla de perímetros se puede desplegar o limpiar una grilla automática de bots en modo espectador posicionados en \yellowY=128\reset para mantener cargados los chunks del perímetro mientras trabaja la máquina.
