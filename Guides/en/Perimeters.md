\gold\boldPERIMETERS AND WORLD EATER\reset

The perimeter system registers World Eater areas, monitors excavation progress down to a target Y level, sends stall alerts to Discord, and deploys a grid of spectator bots to keep chunks loaded.

Administration must enable \yellowcommandPerimeters\reset with Carpet. Discord notifications also require the \yellowworld-eater.py\reset plugin and the \yellowWorldEater\reset configuration in \yellowAeternumBot\reset.

—————————————————————————————————
\aqua\boldCOMMANDS AND INTERFACE\reset
—————————————————————————————————

\yellow/perimeter\reset — \redOP ONLY\reset
Opens the visual screen (\yellowPerimetersScreen\reset) to review registered perimeters, edit region bounds (\yellowRegión\reset, keeping the initial reference with \yellowRestaurar\reset), start or \yellowCancelar\reset scans, adjust target Y or stall timeout, and control the bot grid. Requires the Aeternum Carpet client.

When a completed scan exists and palette blocks are created or broken inside the area, the button displays \yellowUpdate (N)\reset and re-scans only those modified chunks.

\yellow/perimeter add <name> <x1> <z1> <x2> <z2>\reset — \redOP ONLY\reset
Registers a new rectangular perimeter between both X/Z coordinates.

\dark_grayExample: /perimeter add main_we -500 -500 500 500

The name only allows lowercase letters, numbers, underscores and hyphens (max 48 characters), and the maximum allowed area is \yellow200,000,000 blocks\reset.

—————————————————————————————————
\aqua\boldALERTS AND MONITORING\reset
—————————————————————————————————

\dark_gray• \whiteTarget Y:\reset minimum height the excavation must reach before notifying completion.
\dark_gray• \whiteStall timeout:\reset seconds without progress before triggering a stall alert.
\dark_gray• \whiteDiscord alerts:\reset \yellowAeternumBot\reset forwards alerts to the channel set in \yellowWorldEater.Channel ID\reset and via DM when \yellowWorldEater.Allow DM\reset is enabled in \yellow/config\reset.

—————————————————————————————————
\aqua\boldSPECTATOR BOT GRID\reset
—————————————————————————————————

From the perimeter screen you can spawn or clear an automatic grid of spectator bots positioned at \yellowY=128\reset to keep the perimeter chunks loaded while the machine runs.
