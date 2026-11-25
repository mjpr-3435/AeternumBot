\gold\boldGENERAL BACKUPS\reset

A general backup copies the entire server: world, configurations and process files. It is different from a regional backup, which only saves chosen regions.

—————————————————————————————————
\aqua\boldFOR EVERYONE\reset
—————————————————————————————————

\yellow!!bk\reset or \yellow!!bk help\reset
Shows help.

\yellow!!bkps\reset
Lists available backups with date, author and comment if it exists.

\yellow!!mk-bkp [comment]\reset
Creates a full backup. The server saves the world before copying it, warns players and only allows one copy at a time.

\dark_grayExample: !!mk-bkp before_updating_spawn

—————————————————————————————————
\aqua\boldHOW THEY ARE SAVED\reset
—————————————————————————————————

The current configuration keeps \yellow3 manual backups\reset: the SMP 1, SMP 2 and SMP 3 slots. Each new manual backup occupies the most recent slot and the previous ones shift.

When those three slots are full, the system rotates an old one to make space. If there is any backup created by an administrator, it always protects at least the most recent administrative backup during that rotation.

\aquaExample:\reset there are three manual backups. The oldest was created by an admin; the other two are from users. When creating a new one, normally the oldest would be deleted, but in this case the administrative one is preserved and the oldest user backup is discarded.

\dark_grayThe names SMP 1, 2 and 3 are reordered after each copy. To identify a backup, check date and author with !!bkps, not just its number. There are always three manuals; the fourth slot is exclusively the automatic one.

—————————————————————————————————
\aqua\boldAUTOMATIC BACKUP\reset
—————————————————————————————————

The automatic backup uses a separate slot: \yellowSMP 4\reset. If a valid one does not exist, it is created when the system starts; then it is replaced approximately every 24 hours.

\dark_grayThere is only one automatic copy. The next run replaces SMP 4; it does not occupy or rotate the three manual slots.

It also saves the world and warns while working. If a manual backup is in progress, it waits before trying again.

\red\boldThe automatic helps with recent accidents, but create a manual one before an update, restoration or cleanup.\reset

—————————————————————————————————
\red\boldADMINISTRATION ONLY\reset
—————————————————————————————————

\yellow!!load-bkp <name>\reset
Prepares loading a full backup.

\yellow!!bk confirm\reset
Confirms the load. The server warns everyone, waits 5 seconds, stops, restores files and starts again.

\yellow!!del-bkp <name>\reset
Permanently deletes a full backup.

\dark_grayRestoring replaces the current server state, not just the world. Check name, date, author and comment with !!bkps before confirming.
