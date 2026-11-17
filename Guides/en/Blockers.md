\gold\boldBLOCKERS\reset

Blockers searches within an area for blocks that can stop, interfere with or make a piston mechanism unsafe. The analysis does not break, move or replace blocks: it only records positions so they can be reviewed and marked.

For the system to exist, administration must activate \yellowcommandBlockers\reset with Carpet. Once active, players and OPs share the same query interface, but not the same controls.

—————————————————————————————————
\aqua\boldWHAT COUNTS AS A BLOCKER\reset
—————————————————————————————————

A result appears for one of two reasons:

\dark_gray• The block is in the configured blocker list.
\dark_gray• The block has the waterlogged property, meaning it contains water.

The initial list includes obsidian, crying obsidian, ender chest, bedrock, reinforced deepslate, end portal frame and end portal block. Administration can adjust it; waterlogged blocks are always detected because they can also affect mechanisms.

Results save the block type, its coordinates and the reason. An analysis belongs to the dimension where it was requested: Overworld, Nether and End are checked separately.

—————————————————————————————————
\green\boldFOR PLAYERS\reset
—————————————————————————————————

\yellow/blockers\reset
Opens the list of existing analyses. Select one to see its blockers, how many it found and whether it is still working. Everyone can view results, even if another person requested the analysis.

\yellow/blockers <coord1> <coord2> <name>\reset
Requests an analysis of the cube between both coordinates, in the current dimension.

\dark_grayExample: /blockers 100 60 -80 180 100 0 north_farm

The name identifies the analysis, so it must be unique and can only contain lowercase, numbers, underscores and hyphens. The system rejects duplicate names: do not reuse one from a previous scan without asking an OP to delete that record.

Each analysis can cover at most \yellow200,000,000 blocks\reset. It sounds high, but it is still a big job: the server loads and reads the necessary chunks little by little. Do not request a huge box "just in case"; delimit the machine or build you actually need to review.

To keep the server stable, each player can have \yellowone pending analysis\reset at a time and the server supports \yellowfour pending\reset in total. When a scan finishes, you can request another. While it progresses, whoever requested it receives progress in chat; when finished, everyone receives a notification.

\aqua\boldREADING AN ANALYSIS\reset

Inside an analysis, each row shows:

\dark_gray• \whiteBlock\reset: the type of block found.
\dark_gray• \whiteCoordinates\reset: its exact position.
\dark_gray• \whiteReason\reset: whether it comes from the blocker list or from being waterlogged.

You can click on one or several rows. The chosen blocks appear in the world as semi-transparent purple boxes, visible even through walls. It is a personal visual guide: it is not shared, does not grant additional permissions and does not modify the block.

\yellowSelect all\reset marks all results of that analysis. \yellowClear selection\reset turns off the purple boxes. They are also cleared if the result stops existing in the registry, for example after breaking the block or deleting the analysis.

The list has mouse wheel scrolling and a draggable bar when there are more results than fit on screen. Use the back button to return to the scan list or the X to close the interface.

—————————————————————————————————
\red\boldADMINISTRATION ONLY\reset
—————————————————————————————————

OPs manage what counts as a blocker and which analyses remain saved. Players can request and read scans, but not change this shared data.

\yellow/blockers list\reset
Shows the current list of block types that Blockers considers configured. Any player can see it; it helps to know what the next scan will look for.

\yellow/blockers list add <block>\reset — \redOP ONLY\reset
Adds a block type to the list. Accepts full ids, like \yellowminecraft:slime_block\reset, or short vanilla names when applicable. Future analyses will take the block into account; an already finished analysis is not automatically recalculated.

\yellow/blockers list remove <block>\reset — \redOP ONLY\reset
Removes a block type from the list. It does not delete blocks from the world or erase already saved results; it only changes analyses made afterwards.

\aqua\boldDELETING AN ANALYSIS\reset

In the scan list, OPs see an X to the right of each analysis. They must hold \yellowShift\reset while clicking to activate it. This prevents accidental deletion.

Deleting a scan removes its record and its results; it does not modify any block in the world. If the analysis was still pending, it also cancels its work in the queue. Everyone receives a message indicating it was deleted.

—————————————————————————————————
\aqua\boldWHEN TO RE-ANALYZE\reset
—————————————————————————————————

Results update if a player breaks one of the found blocks: that entry disappears from the analysis. However, placing new blocks, changing waterlogged state or modifying a large part of the area does not automatically complete the record. For a faithful review after major changes, create a new scan with a different name or ask an OP to delete the previous one and reuse its name.

\dark_grayRecommendation: use one name per machine and revision, for example iron_farm_v1 or storage_east_2026. This way it is clear which build each result represents.

—————————————————————————————————
\red\boldBEST PRACTICES\reset
—————————————————————————————————

Select the smallest useful volume, wait for it to finish before requesting another review and do not use Blockers as a global world search. If you don't know which block is stopping a machine, first review a specific section and use the purple boxes to reach the candidates before modifying anything.
