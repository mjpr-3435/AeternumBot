\gold\boldFINDER: SEARCH IN STORAGE\reset

Finder allows locating and counting items within registered storage areas. It is a query tool: it does not move, consume or modify items. Administration defines the areas; any player can search in any registered area.

The \yellowcommandFinder\reset rule must be active. Finder saves the areas, their dimension and exclusions in the world.

—————————————————————————————————
\green\boldFOR EVERYONE: SEARCHING AND COUNTING\reset
—————————————————————————————————

\yellow/find <place> <item>\reset
Searches for the item in the indicated storage area (with place autocomplete). You can also use \yellownear_me\reset as the place to search containers within a 20-block radius around you without needing a registered area. Shows each container that has it, with block type, coordinates and quantity. Also draws a temporary path with particles and markers to reach nearby matches.

\dark_grayExamples: /find MainStorage redstone · /find near_me stone · /find MainStorage ender chest

\yellow/count <place> <item>\reset
Counts the total items and stacks of the item within the indicated area or in \yellownear_me\reset (20-block radius). It does not create markers or a path; it is the quick option when you only need to know how much there is.

\dark_grayExamples: /count MainStorage firework rockets · /count near_me redstone

Finder understands technical ids like \whiteminecraft:redstone\reset, names in Spanish and normal names with spaces. It is case-insensitive and normalizes accents when searching.

\aqua\boldRESULT OF A SEARCH\reset

\yellow/find\reset lists each match and then reports how many containers it found. The path and markers are private to the searcher and last approximately eight seconds. If a result is very far away, it may appear listed but not receive a direct line: the visual guide prioritizes nearby targets to avoid overwhelming the client.

\yellow/count\reset reports two amounts:

\dark_gray• Items: total number of units.
\dark_gray• Stacks: number of stacks containing that item.

Shulkers are also checked internally, even when they are inside chests or other shulkers. For example, redstone stored inside a shulker placed in a chest does count for \yellow/find MainStorage redstone\reset and \yellow/count MainStorage redstone\reset.

\aqua\boldWHEN THE RESULT UPDATES\reset

Finder re-reads the entire area before each \yellow/find\reset and \yellow/count\reset. It does not keep an inventory cache between queries.

That is why an item you just moved is reflected in the next search. The query may take a little longer than a cache-based response, especially in a large area, but the result corresponds to the state Finder just read.

—————————————————————————————————
\red\boldADMINISTRATION ONLY: AREAS\reset
—————————————————————————————————

\yellow/finder help\reset
Shows a brief reminder of Finder administration commands.

\yellow/finder scan <coord1> <coord2> <name>\reset
Creates a new area or rescans an existing one. The cube includes all blocks between both coordinates and is saved in the current dimension.

\dark_grayExample: /finder scan 0 50 0 127 100 127 MainStorage

The name must use only letters (a-z, A-Z) and numbers (0-9), with no spaces or symbols. An area supports a maximum of 10,000,000 blocks and 256 chunks, equivalent at most to a 16 × 16 chunk grid. Use a tight selection: scanning a huge area loads more chunks and takes longer, even if done gradually.

The scan checks one full chunk per tick and sends progress to the OP who requested the scan approximately every two seconds. When finished it reports how many containers it found.

Finder recognizes chests, trapped chests, barrels, dispensers, droppers and all placed shulkers. Other inventories, such as hoppers, are not currently included: use \yellow/finder check\reset if you have doubts about a block.

\yellow/finder list\reset
Shows all saved areas, their dimension and number of containers. Each line includes chat buttons:

\dark_gray• ↻: rescan it with the same coordinates.
\dark_gray• X: delete it.

\yellow/finder remove <name>\reset
Removes the area from the registry. It does not break chests or change blocks; it just stops being used in Finder.

—————————————————————————————————
\aqua\boldCHECKING AND EXCLUDING BLOCKS\reset
—————————————————————————————————

\yellow/finder check [coordinates]\reset
Checks whether the block under your feet —or the indicated coordinates— is a container type supported by Finder. Marks it briefly with green particles if it enters the scan or red if it does not.

\yellow/finder toggle-block [coordinates]\reset
Excludes or re-includes that block from all registered areas containing it. Without coordinates it uses the block under your feet. Useful for ignoring a specific chest without reducing or splitting the entire area.

\yellow/finder show_excludes\reset
Lists excluded positions, grouped by area.

\yellow/finder clean\reset
Removes all loaded \whiteminecraft:block_display\reset entities and clears Finder's temporary paths and markers. Useful if a marker was left behind after a restart or chunk unload.

Exclusions persist and are respected when rescanning. If the same position belongs to more than one area, \yellowtoggle-block\reset changes its status in all of them; check \yellowshow_excludes\reset if you work with overlapping areas.

—————————————————————————————————
\aqua\boldRESCANNING AND MAINTAINING\reset
—————————————————————————————————

Rescan an area when chests, barrels, placed shulkers or any storage structure are added or removed. Queries read the containers at that moment, but do not automatically discover a new chest that was never in the initial scan.

Normal inventory changes appear in the next search. For structural changes, use the ↻ button from \yellow/finder list\reset or repeat \yellow/finder scan\reset with the same coordinates and name.

\dark_grayRecommended workflow:
\dark_gray1. Scan each warehouse with a clear name (letters and numbers only).
\dark_gray2. Check the areas with /finder list.
\dark_gray3. Test /find <place> and /count <place> with a known item.
\dark_gray4. Exclude chests that should not participate.
\dark_gray5. Rescan after expanding or redesigning the storage.

Finder works best with well-defined areas per warehouse, not with a selection that tries to cover all the chests on the server.
