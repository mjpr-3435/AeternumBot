\gold\boldSERVER MANAGEMENT\reset

These commands control processes managed by AeternumBot: servers and networks.

—————————————————————————————————
\aqua\boldFOR EVERYONE\reset
—————————————————————————————————

\yellow!!pm help\reset
Shows available help.

\yellow!!status\reset
Shows CPU, RAM, disk and the status of each process. Hover over the indicators to see details.

\yellow!!start <process>\reset
Starts a stopped process.

\dark_grayExamples: !!start SMP, !!start MMP, !!start CMP

If the process was already running, it does not start a second time. You can check status and start a stopped one, but you cannot stop or restart processes belonging to others.

—————————————————————————————————
\red\boldADMINISTRATION ONLY\reset
—————————————————————————————————

\yellow!!stop [process]\reset
Stops the indicated process. Without an argument, stops the current server.

\yellow!!restart [process]\reset
Restarts the indicated process. Without an argument, restarts the current server.

\yellow!!mdreload [process]\reset
Reloads mdplugins. Without an argument, those of the current server. Applies updated commands and automations without restarting Minecraft when the plugin allows it.

\yellow!!adreload\reset
Reloads AeternumBot's mdaddons. Can re-sync managed plugins and guides.

\red\boldBefore stopping or restarting, warn others and check !!status. A restart cuts connections and can cancel backups, updates or cleanups in progress.\reset
