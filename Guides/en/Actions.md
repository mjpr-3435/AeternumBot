\gold\boldACTION PACKAGES\reset

Actions allows saving sequences of server commands under a name and executing them from a panel or by typing \yellow!!Package name\reset. It is useful for repeatable automations: preparing an event, controlling bots, activating mechanisms or running several commands in a defined order.

The \yellowcommandActions\reset rule must be active. Packages are saved in the world, in \yellowworld/data/aeternum_command_packs.json\reset, and the server is the source of truth. To use the panel, Aeternum Carpet is needed on both client and server.

\red\boldIMPORTANT\reset
Each command in a package is executed as the server. It does not use the permissions of the player who pressed Run. That is why any available package must be safe for any player to execute.

—————————————————————————————————
\green\boldFOR EVERYONE: VIEWING AND RUNNING\reset
—————————————————————————————————

\yellow/actions\reset
Opens the package catalog. The list is sorted alphabetically and the Filter by title field allows typing part of the name to show only matches.

Click on a row to open the package. Without OP it opens in read-only mode: you can review the name, description, type of each step and its content, but not change anything.

\yellow▶ Run\reset
The ▶ button to the right of a package starts it. There is also a \yellowRun\reset button inside a package view. If that same package is already running, the server rejects it to avoid duplication.

\yellow!!<full package name>\reset
Runs a package directly from chat. The name must be complete, but is case-insensitive: \yellow!!bedbot on\reset and \yellowBedBot ON\reset find the same package. If it does not exist, or is already running, the executor receives the corresponding notice.

\aqua\boldWHAT YOU SEE WHEN RUNNING\reset

All connected players receive Actions notifications:

\dark_gray• On start: the name of the package being executed.
\dark_gray• For each command: ✓ if the server accepted it or ✕ if it failed, followed by the command.
\dark_gray• At the end: \greenAction finished.\reset

The ✓ symbol confirms the command returned success to the server; it does not replace checking the result in the world when an order depends on entities, conditions, permissions or external data. If a step fails, Actions marks it with ✕ and continues with the next step. A failure does not automatically cancel the entire package.

\aqua\boldWAITS AND PACING\reset

Actions processes work gradually: it does not block the server while waiting. A wait is counted in seconds and lets that time pass before continuing. Commands are queued in the normal server cycle, which avoids locks with Carpet commands like \yellow/player ... spawn\reset.

A package can run while a different package is active. Avoid creating packages that compete for the same bot, entity, area or mechanism: Actions maintains order within each package, it does not resolve conflicts between different packages.

—————————————————————————————————
\red\boldADMINISTRATION ONLY: CREATING AND EDITING\reset
—————————————————————————————————

OPs see \yellow+ New package\reset in the catalog and can edit any package. Editing is not published until pressing \yellowSave\reset; exiting with Escape or closing the editor discards unsaved changes from that editing session.

\aqua\boldCREATING A PACKAGE\reset

1. Open \yellow/actions\reset and press \yellow+ New package\reset.
2. Write a clear name and an optional description.
3. Press \yellow+ New line\reset to create the first step.
4. Add commands and waits in the required order.
5. Press \yellowSave\reset.
6. Run it once and review the feedback before announcing it to players.

The name is mandatory, supports up to 80 characters and must be unique ignoring case. You cannot have \whiteBed\reset and \whitebed\reset as separate packages. The description supports up to 240 characters and only documents the package: it is not executed.

\aqua\boldADDING AND EDITING STEPS\reset

\yellow+ New line\reset adds a command step at the end. Each package allows up to 128 steps.

Each line has a selector:

\dark_gray• \yellowCMD\reset: the line is a server command.
\dark_gray• \yellowWAIT\reset: the line is a duration in seconds.

Press CMD or WAIT to change the line type. When switching to wait, the initial value is 1 second; when switching back to command, the initial value is \whitesay \reset. Write the final value before saving.

A command supports up to 2048 characters. You can write it with or without an initial /: Actions strips a leading / before sending it to the server. Do not paste several orders separated by line breaks in a single CMD; use one line per order so that feedback and waits make sense.

A wait supports from 0 to 3600 seconds. \yellow0\reset does not add a useful pause, but is valid. To wait more than one hour, use several wait lines and make the reason clear in the description.

When there are more than six steps, use the scroll wheel over the list or drag its bar to reach the others. Before scrolling, the editor preserves the value of the line you were editing.

\aqua\boldSAVING AND VALIDATING\reset

\yellowSave\reset activates only when there are pending changes. When pressed, the server validates all packages: unique names, mandatory fields, text limit, type of each step and valid seconds.

If rejected, check the \redData rejected\reset message or the editor notice. A partial version is not saved: fix the problem and press Save again.

When saving, the catalog is sorted alphabetically and all connected players receive the updated version. This allows them to run the new package without reconnecting.

\aqua\boldDELETING\reset

In the main list, the X for each package requires holding \yellowShift\reset. In the editor, the \yellowDelete\reset button also requires Shift. Deletion removes the saved package and has no recycle bin or additional confirmation.

Do not delete a package that is being used or documented without warning. If you only want to temporarily withdraw it, change its name or description explicitly and save; remember it remains executable while it stays in the catalog.

—————————————————————————————————
\aqua\boldDESIGNING SAFE PACKAGES\reset
—————————————————————————————————

\dark_gray• Use names that explain the effect: open_event, stop_miner_bot or restart_tnt_duper.
\dark_gray• Describe who it affects and what condition must be met before running it.
\dark_gray• Start with a harmless warning command if the package does something important.
\dark_gray• Separate actions that need real time with WAIT, not with repeated commands.
\dark_gray• Test each package in a safe environment or with a small version before making it visible to everyone.
\dark_gray• Avoid destructive or irreversible orders in a public package. If they are unavoidable, do not leave it available for normal players to run.

Actions is designed for public and reviewed packages. Since anyone can launch them, security is not about who clicks: it is about which commands administration decided to save.
