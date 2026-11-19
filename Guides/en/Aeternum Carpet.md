\gold\boldAETERNUM CARPET · GENERAL GUIDE\reset

Aeternum Carpet adds its own rules and commands to Carpet. This guide is the quick reference: it indicates what each rule does, which commands it enables and who can use them.

\greenFOR EVERYONE\white means any player with normal command access. \redOP ONLY\white means operator level 2 or higher. A command only exists while its rule is enabled.

—————————————————————————————————
\aqua\boldRULES: ENABLE, QUERY AND SAVE\reset
—————————————————————————————————

\yellow/carpet <rule> <value>\reset — \redOP ONLY\reset
Changes a rule. For boolean rules use \yellowtrue\reset or \yellowfalse\reset.

\dark_grayExample: /carpet commandFinder true

\yellow/carpet <rule>\reset — \redOP ONLY\reset
Shows the value and description of a specific rule.

\yellow/carpet list aeternum\reset — \redOP ONLY\reset
Shows all rules added by Aeternum Carpet.

\yellow/rules\reset — \redOP ONLY\reset
Opens the visual interface to browse, search, filter and edit all Carpet rules and its extensions, including resetting to default and saving to the server configuration. Requires the Aeternum Carpet client.

Changes are saved in the server's Carpet configuration. By default \yellowjoinMotd\reset, \yellownaturalIceFormation\reset and \yellowallowPlayerExploration\reset are enabled. Command tools and \yellowexplorationManager\reset start disabled.

—————————————————————————————————
\aqua\boldDIRECT MECHANICS\reset
—————————————————————————————————

\yellowspectatorPortalTravel\reset — disabled by default
Allows spectator players to go through portals like a normal player. Portal detection works from the player's eye level, so flying head-first into a portal activates it immediately. Does not grant spectator or change permissions; only modifies that portal behavior.

\yellowopenShulkerInHand\reset — disabled by default
Allows opening a shulker when used in the air while held in hand. The main hand has priority: if you hold a shulker in the main hand, it opens regardless of what the offhand holds.

\yellow/quickshulker\reset — \greenFOR EVERYONE\reset
Enables or disables quick shulker access for whoever runs the command. The rule must be active; it does not affect other players' preferences.

\yellowopenEnderChestInHand\reset — disabled by default
Allows opening an Ender chest when used in the air while held in hand. Like the shulker, the main hand takes priority.

\yellow/quickenderchest\reset — \greenFOR EVERYONE\reset
Enables or disables quick Ender chest access for whoever runs the command. The rule must be active.

If you have a shulker in the main hand and an ender chest in the offhand (or vice versa), the main hand item opens. The other item's action is cancelled.

\yellowinstamineDeepslate\reset — disabled by default
Allows breaking deepslate instantly only with a netherite pickaxe, Efficiency V and Haste II or higher. Does not remove tool requirements or alter drops.

\yellowfastObsidian\reset — disabled by default
Obsidian and crying obsidian break at the same speed as stone with a netherite pickaxe and Efficiency V. Does not instamine them: only matches the break time to stone with the same tools. Does not require haste.

\yellowbreakEndPortalFrames\reset — disabled by default
Allows breaking end portal frames through sustained mining with a mace, Breach IV, Haste II and Strength II. It is a very specific administrative tool, not a normal frame breaking.

\yellowbreakEndPortalsWithWindCharge\reset — disabled by default
Allows a wind charge to remove end portal blocks within a small area. Useful for dismantling an active portal without editing world files.

\yellowallowUnlimitedPlayerSpeed\reset — disabled by default
Disables the vanilla check that pushes back a player for moving too fast. Only use it if a legitimate server mechanic needs very fast movements: it also stops applying that movement protection.

\yellownaturalIceFormation\reset — enabled by default
When active, water freezes naturally under vanilla conditions. In \yellowfalse\reset it prevents natural ice formation; player-placed ice is not modified.

\yellowprotectedPots\reset — disabled by default
Prevents \yellowminecraft:decorated_pot\reset from breaking when a player collides with them while flying with elytra boosted by a firework rocket. Other breaks (arrows, tridents, explosions, pistons and manual mining) keep working as in vanilla.

\yellowphantomSpawning\reset — default value: \yellowvanilla\reset
Controls natural phantom spawning.

\dark_gray• \yellowvanilla\reset: normal Minecraft behavior.
\dark_gray• \yellowmobcap\reset: phantoms respect the hostile mob cap.
\dark_gray• \yellowdisable\reset: phantoms do not spawn naturally.

\yellowcraftableCalcite\reset — disabled by default
Enables crafting 2 calcite blocks in a crafting table or crafter using 4 amethyst shards in the corners, 4 nether quartz on the edges, and 1 smooth basalt in the center.

—————————————————————————————————
\aqua\boldWELCOME MESSAGE AND TASKS\reset
—————————————————————————————————

\yellowjoinMotd\reset — enabled by default
Shows the welcome banner upon joining and enables the following commands.

\yellow/motd\reset — \greenFOR EVERYONE\reset
Shows the personal welcome banner again.

\yellow/motd tasks\reset — \greenFOR EVERYONE\reset
Shows the current public tasks. Does not modify anything.

\yellow/motd add <text>\reset — \redOP ONLY\reset
Adds a public task to the banner. Rejected if empty, exceeds the limit or the maximum number of tasks has already been reached.

\yellow/motd delete <number>\reset — \redOP ONLY\reset
Deletes the indicated public task. Afterwards shows the list again to confirm the resulting state.

—————————————————————————————————
\aqua\boldPERSONAL LIST\reset
—————————————————————————————————

\yellowcommandTodoList\reset enables \yellow/todo\reset. Notes are personal: neither OP nor other players see or modify someone else's list.

\yellow/todo\reset or \yellow/todo list\reset — \greenFOR EVERYONE\reset
Shows your numbered notes. Each line includes a clickable X to delete that note.

\yellow/todo add <text>\reset — \greenFOR EVERYONE\reset
Adds a note to your list. The full text, including spaces, is stored as a single note.

\yellow/todo delete <number>\reset — \greenFOR EVERYONE\reset
Deletes a note by its number and shows the updated list again.

—————————————————————————————————
\aqua\boldSERVER GUIDES\reset
—————————————————————————————————

\yellowcommandGuide\reset enables \yellow/guide\reset. Guides are world files and the server is the source of truth: players receive the content when opening the panel, they do not need to download a guide manually.

Guides are organized by language in \yellowes/\reset and \yellowen/\reset subdirectories inside \yellowworld/data/aeternum_guides\reset. When opening \yellow/guide\reset Spanish is loaded by default. The \yellow[ES]\reset and \yellow[EN]\reset buttons in the upper corner switch between languages.

\yellow/guide\reset — \greenFOR EVERYONE\reset
Opens the guide library within the game. Allows reading, scrolling through long texts, choosing another guide and switching languages. Requires the Aeternum Carpet client to display the interface.

\dark_grayIn the library, OPs see Edit and Refresh; others only read.

\greenIN THE EDITOR — OP ONLY\reset

\dark_gray• Create: creates an empty guide with a unique title.
\dark_gray• Edit: content is automatically saved while typing.
\dark_gray• Rename: changes the title and file when a new name is pending.
\dark_gray• Reorder: each row in the list has ▲ and ▼ to move up or down one position.
\dark_gray• Delete: deletes the selected guide (requires holding Shift).
\dark_gray• Refresh: re-reads server files and detects changes made outside the game.

The ? button shows syntax help within the interface itself.

—————————————————————————————————
\aqua\boldACTION PACKAGES\reset
—————————————————————————————————

\yellowcommandActions\reset enables \yellow/actions\reset. A package contains command and wait steps; commands are executed as server, one after another. A package cannot duplicate another's name ignoring case: \yellowBed\reset and \yellowbed\reset are not two distinct valid names.

\yellow/actions\reset — \greenFOR EVERYONE\reset
Opens the package list. Everyone can filter, review a package and run an available one. Execution notifies all players which command started, whether it finished correctly and if it failed.

\yellow!!<full package name>\reset — \greenFOR EVERYONE\reset
Directly runs a package from chat. Matching is case-insensitive; for example \yellow!!bedbot on\reset finds \yellowBedBot ON\reset. The full name must be written after \yellow!!\reset.

\redIN THE EDITOR — OP ONLY\reset

\dark_gray• New package: creates a package with name and description.
\dark_gray• Add line: adds a command or wait step.
\dark_gray• Edit a line: changes the order or wait duration.
\dark_gray• Save: activates only if there are pending changes; keeps the current screen when saving.
\dark_gray• Delete package or command: requires holding Shift and being OP.

A wait uses seconds. Before saving, review destructive commands, permissions, order and target: Actions does not ask for additional confirmation when a package is executed.

—————————————————————————————————
\aqua\boldBLOCKERS\reset
—————————————————————————————————

\yellowcommandBlockers\reset enables \yellow/blockers\reset. It is used to search for blocks configured as blockers within a selection; the analysis is saved and can be reviewed in the interface.

\yellow/blockers\reset — \greenFOR EVERYONE\reset
Opens the analysis interface. Any player can review analyses and results. Only OP sees and can use the delete X, while holding Shift.

\yellow/blockers list\reset — \greenFOR EVERYONE\reset
Shows the block types that are considered blockers.

\yellow/blockers list add <block>\reset — \redOP ONLY\reset
Adds a valid block to the list. Accepts a full id like \yellowminecraft:slime_block\reset or the short vanilla name when possible.

\yellow/blockers list remove <block>\reset — \redOP ONLY\reset
Removes a block from that list. Subsequent analyses will no longer count it.

\yellow/blockers <coord1> <coord2> <name>\reset — \greenFOR EVERYONE\reset
Starts the analysis of the cube between both coordinates in the current dimension. The name uses lowercase, numbers, _ or - and cannot be repeated. Each analysis can cover up to 25,000,000 blocks. Each player can only have one pending and the server supports a maximum of four pending to avoid an absurd queue; the result reports how many chunks will be analyzed.

—————————————————————————————————
\aqua\boldMATERIALS: PROJECT COLLECTION LISTS\reset
—————————————————————————————————

\yellowcommandMaterials\reset enables \yellow/materials\reset. Lists are CSV files in \yellowworld/data/aeternum_materials/\reset and compare the target amounts against what is stored and what each player carries.

\yellow/materials\reset — \greenFOR EVERYONE\reset
Opens the material lists. The detail screen shows each item with its Total, Missing and who claimed it.

\yellow/materials storage add <list> <coord1> <coord2>\reset — \redOP ONLY\reset
Assigns the storage area of a list. Each list has a single storage area: if it already has one, the command is rejected until it is removed.

\yellow/materials storage list\reset — \redOP ONLY\reset
Shows the assigned storage areas with a clickable X to remove one.

\yellow/materials storage del <list> <index>\reset — \redOP ONLY\reset
Removes the indicated storage area.

The detail screen orders items in two groups: missing first and completed afterwards, both by total from largest to smallest. Quantities use progressive units: loose items, stacks (64 x N + Y), \yellowSB\reset (1 shulker = 1,728 items) and \yellowSDC\reset (a double chest of shulker boxes = 93,312 items).

The HUD overlay shows your claimed items still missing; the count is server-side and also considers what you carry in your inventory, including shulkers. See the \whiteMaterials\dark_gray guide for the full details.

—————————————————————————————————
\aqua\boldFINDER: SEARCH IN STORAGE\reset
—————————————————————————————————

\yellowcommandFinder\reset enables Finder. It has two levels: queries for everyone and area administration for OP. Finder does not move or modify items. Each query re-reads containers before responding.

\yellow/find <place> <item>\reset — \greenFOR EVERYONE\reset
Searches for the item in the indicated area (with place autocomplete) or in \yellownear_me\reset (20-block radius around the player). Shows each matching container, quantity and coordinates; for a player also marks a temporary path with particles and markers.

\yellow/count <place> <item>\reset — \greenFOR EVERYONE\reset
Counts the total and stacks of the item in the indicated area or in \yellownear_me\reset, without sending the particle path.

\yellow/finder scan <coord1> <coord2> <name>\reset — \redOP ONLY\reset
Creates or updates an area (the name only allows letters a-z, A-Z and numbers 0-9). Only up to 256 chunks and 10,000,000 blocks are scanned. Scanning progresses incrementally without preview particles.

\yellow/finder list\reset — \redOP ONLY\reset
Lists areas. Includes chat buttons: ↻ rescans and X deletes the area.

\yellow/finder remove <name>\reset — \redOP ONLY\reset
Deletes a registered area.

\yellow/finder check [coordinates]\reset — \redOP ONLY\reset
Checks whether a block is a supported container and highlights it.

\yellow/finder toggle-block [coordinates]\reset — \redOP ONLY\reset
Includes or excludes a block from all areas containing it.

\yellow/finder show_excludes\reset — \redOP ONLY\reset
Shows excluded blocks for each area.

\yellow/finder clean\reset — \redOP ONLY\reset
Removes all loaded \yellowminecraft:block_display\reset entities and clears temporary Finder markers.

—————————————————————————————————
\aqua\boldBLOCK PROTECTION\reset
—————————————————————————————————

\yellowcommandProtect\reset enables \yellow/protect\reset. It is a persistent protection for specific blocks, not a claims system or a full protected region.

\yellow/protect add [coordinates]\reset — \redOP ONLY\reset
Protects the looked-at block up to six blocks away. If coordinates are given, protects exactly that block. Does not allow protecting air.

\yellow/protect remove [coordinates]\reset — \redOP ONLY\reset
Removes protection from the looked-at block or the indicated coordinates.

\yellow/protect list\reset — \redOP ONLY\reset
Shows all protected blocks, with dimension and coordinates.

—————————————————————————————————
\aqua\boldEXPLORATION MANAGEMENT\reset
—————————————————————————————————

\yellowexplorationManager\reset enables \yellow/exploration\reset, its regions, pregeneration and the map.

\yellow/exploration map\reset — \greenFOR EVERYONE\reset
Opens the topographic map. Allows dragging to navigate, scroll wheel to zoom, Space to return to 0,0 and F to center on your own position. A single \yellowDim\reset button cycles between Overworld, Nether and End. The top bar shows the server MSPT in real time. Requires Aeternum Carpet client.

OPs can create regions by right-click dragging on the map. The interface includes buttons to adjust \yellowReq\reset (maximum simultaneous tiles), \yellowClear all\reset (wipe dimension cache) and \yellowClear screen\reset (clear only visible tiles). Regions are now rectangular: dragging defines corners, not a center and radius.

\yellow/exploration pregen start\reset — \redOP ONLY\reset
Starts or resumes the pregeneration queue of registered regions. Progress is preserved between restarts.

\yellow/exploration pregen pause\reset — \redOP ONLY\reset
Pauses the queue without discarding progress.

\yellow/exploration pregen stop\reset — \redOP ONLY\reset
Stops the queue and discards its saved progress. Only use it if you want to start over.

\yellow/exploration pregen status\reset — \redOP ONLY\reset
Shows state, progress and current pregeneration pace.

\yellow/exploration pregen speed <1-1200>\reset — \redOP ONLY\reset
Sets the maximum chunks per minute. The system does not always use that maximum: it works only with low and stable MSPT, below 20 ms, to avoid turning lag spikes into additional load.

\yellowallowPlayerExploration\reset controls the generation limit outside regions. In \yellowtrue\reset it allows normal exploration. In \yellowfalse\reset it limits generation to registered regions, provided the exploration manager is not active; while \yellowexplorationManager\reset is running, that barrier is temporarily disabled to avoid interfering with management and pregeneration.

The selection is automatically exported per dimension for external world maintenance. It does not require a manual export command.

—————————————————————————————————
\aqua\boldKEYBINDS\reset
—————————————————————————————————

Aeternum Carpet registers keybinds in \yellowOptions → Controls → Aeternum\reset to open the screens directly, without typing a command:

\dark_gray• Open /blockers
\dark_gray• Open /guide
\dark_gray• Open /materials
\dark_gray• Open /exploration map
\dark_gray• Open /actions

By default they have no key assigned: each player chooses their own. Pressing a key asks the server to open that screen; it only works if the corresponding rule is active.

—————————————————————————————————
\red\boldBEFORE CHANGING ANYTHING\reset
—————————————————————————————————

Simple rules can affect everyone immediately. Actions can run server commands, Exploration can generate many chunks and administrative tools change persistent records. Check the active rule, confirm the command and make the appropriate backup before world changes or important automations.
