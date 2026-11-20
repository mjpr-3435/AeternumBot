\gold\boldREGIONAL BACKUPS\reset

A regional backup saves only chosen regions: terrain, POI and entities from Overworld, Nether and End. Each region measures 512 × 512 blocks.

—————————————————————————————————
\aqua\boldSELECT AND CREATE\reset
—————————————————————————————————

\yellow!!rb add\reset
Adds the region where you are standing.

\yellow!!rb pos1\reset and \yellow!!rb pos2\reset
Mark a rectangle in the current dimension. All regions it crosses are added; it does not select exact blocks. Selections are capped at \yellow2,500 regions\reset (50×50, approx. 25.6k × 25.6k blocks).

\yellow!!rb list\reset
Shows the numbered selection by dimension.

\yellow!!rb remove\reset, \yellow!!rb del <number>\reset and \yellow!!rb clear\reset
Remove the current region, a specific entry or your entire selection.

\yellow!!rb mk-bkp <name>\reset
Creates <name>.zip with the selection. The server saves the world before compressing it; only one is created at a time.

\yellow!!rb bkps\reset
Shows regional backups with date, author and included regions.

\yellow!!rb update <name>\reset
Updates the same regions that backup already contained. The creator can update their own; administration or whitelist can update any.

—————————————————————————————————
\red\boldRESTORE AND DELETE\reset
—————————————————————————————————

\yellow!!rb load-bkp <name>\reset and \yellow!!rb confirm\reset
Prepare and confirm restoring a regional backup. The server warns, waits 5 seconds, restarts and loads the files safely.

\yellow!!rb del-bkp <name>\reset
Deletes a backup. The creator can delete their own; administration or whitelist can delete others.

\yellow!!rb load-md\reset
Lists available general backups.

\yellow!!rb load-md <name>\reset and \yellow!!rb confirm-md\reset
Prepare and confirm importing only the regions of your selection from a general backup.

—————————————————————————————————
\aqua\boldPERMISSIONS BY SERVER\reset
—————————————————————————————————

In \yellowSMP\reset, a normal user can select regions, create their own backups, view the list and update or delete only the ones they created. They cannot restore a backup or import regions from a general backup.

The \yellowreg-bkps whitelist\reset grants those sensitive operations without making the player an admin: restoring regional backups, importing regions from general backups and managing others' backups. It does not allow editing the whitelist or grant general administration permissions.

Only SMP administration manages that whitelist:

\yellow!!rb wl list\reset
Shows currently authorized players.

\yellow!!rb wl add <player>\reset
Adds that player to the reg-bkps whitelist.

\yellow!!rb wl remove <player>\reset
Removes that player from the whitelist.

\yellow!!rb wl clear\reset
Empties the entire whitelist. Only use it if you really want to revoke access from all authorized users.

In \yellowMMP, CMP and PMP\reset there are no general backups: regional ones must be used. There any player can prepare and confirm a regional restoration; the whitelist does not limit that restoration. Deleting someone else's backup remains reserved to its creator, administration or whitelist.

\red\boldRestoring replaces entire regions. Check !!rb list and !!rb bkps before confirming.\reset
