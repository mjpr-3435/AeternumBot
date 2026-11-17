\gold\boldEXPLORATION AND PREGENERATION\reset

The Exploration Manager brings together four things: allowed regions, gradual pregeneration, export of the selection for external tools and a topographic map of the already generated world.

Administration must activate \yellowexplorationManager\reset to enable \yellow/exploration\reset. The system saves its regions and configuration on the server; the map and its data come from the server, not the client.

—————————————————————————————————
\aqua\boldIMPORTANT CONCEPTS\reset
—————————————————————————————————

A region has a name, dimension and a rectangle of chunks defined by minimum and maximum corners. Center and radius are no longer used: now you can create non-square regions (for example, 10 × 3 chunks).

Regions do not delete or create blocks by themselves. They are an administrative selection that can be used to limit exploration, export CSV and feed pregeneration.

Names are unique and only accept letters, numbers, _ and -. A region always belongs to the dimension where it was created.

—————————————————————————————————
\green\boldFOR EVERYONE: MAP\reset
—————————————————————————————————

\yellow/exploration map\reset
Opens the topographic map. It shows terrain already saved in the world, with one colored pixel per block and allowed regions in orange. Opening or navigating it does not generate chunks: the server reads existing region files and builds a reusable cache.

\aqua\boldNAVIGATION\reset

\dark_gray• Drag with left click to move the view.
\dark_gray• Use the scroll wheel to zoom in or out. Zoom ranges from 0.0625× to 16× and keeps the point under the cursor.
\dark_gray• Press Space to return to 0,0 and 1× zoom.
\dark_gray• Press F to center the view on your current position.
\dark_gray• The \yellowDim\reset button cycles between Overworld, Nether and End.
\dark_gray• Chunks and Regions activate their grids. Both start turned off.

The top bar shows the server MSPT in real time, the title and dimension, and the block, chunk and region file coordinates under the cursor. The grid buttons do not change the world: they only help measure and orient yourself.

The map delivers 1:1 scale data: one block corresponds to one colored pixel. It does not blend the map according to zoom. In Nether and End it takes the highest available real surface, including constructions above the ceiling.

A gray area normally means a saved chunk does not yet exist or the tile is still arriving; it does not mean the map has generated new terrain.

\aqua\boldADMINISTRATION BUTTONS\reset

OPs see three additional buttons on the bottom bar:

\dark_gray• \yellowReq\reset: controls how many tiles your client can request at once. Click to cycle 4 → 8 → 16 → 32 → 48 → 64. Fewer tiles = less instant load, slower to fill.
\dark_gray• \yellowClear all\reset: wipes all map cache for the current dimension (memory and disk). Tiles will be recalculated when requested again.
\dark_gray• \yellowClear screen\reset: clears only the tiles you are viewing. Useful for forcing a visual refresh without clearing everything.

When clicking any of these buttons, they briefly deactivate (blink) and reactivate on their own, confirming the action was sent.

—————————————————————————————————
\red\boldADMINISTRATION ONLY: REGIONS\reset
—————————————————————————————————

\aqua\boldCREATING FROM THE MAP\reset

Right-click on the map and drag to draw a selection rectangle. When you release, a form opens where you enter the name. The rectangle directly defines the region corners: there is no longer size or radius, just drag what you want to cover.

\dark_gray• If the rectangle exactly matches an existing region, the form opens edit mode (change name or delete).
\dark_gray• If it is a new rectangle, the form creates a new region with those bounds.
\dark_gray• Enter confirms. Escape or X closes without saving.
\dark_gray• When editing, Delete removes the region.

The orange overlay shows each region with its name and dimensions in chunks.

—————————————————————————————————
\aqua\boldAUTOMATIC EXPORT\reset
—————————————————————————————————

Each region change automatically updates three CSVs in the server's \yellowconfig\reset folder:

\dark_gray• ExplorerManagerOverworldSelection.csv
\dark_gray• ExplorerManagerNetherSelection.csv
\dark_gray• ExplorerManagerEndSelection.csv

Each row identifies MCA region and chunk with the format \whiteregionX;regionZ;chunkX;chunkZ\reset. It is the exact selection of registered regions, without an additional 16-chunk margin. These files are the source used by external tools such as world cleanup; you do not need to run an export command.

Do not edit those CSVs to change regions: they are a derived view. Edit regions from the map; the server will rewrite the CSVs correctly.

—————————————————————————————————
\aqua\boldPLAYER EXPLORATION LIMIT\reset
—————————————————————————————————

The \yellowallowPlayerExploration\reset rule controls whether players can leave registered regions.

\dark_gray• In \yellowtrue\reset, exploration works normally.
\dark_gray• In \yellowfalse\reset, a player leaving an allowed region returns to their last valid position in that same dimension and receives a warning.

The restriction only works if there is at least one region in the dimension. If there are none, the server leaves that dimension free to avoid trapping someone without a valid point.

While \yellowexplorationManager\reset is active, the restriction is temporarily disabled. This allows creating, reviewing and pregenerating regions without administration or players being pushed back by the limit. To use the exploration barrier, deactivate the manager after setting up the regions and set \yellowallowPlayerExploration\reset to \yellowfalse\reset.

—————————————————————————————————
\red\boldADMINISTRATION ONLY: PREGENERATION\reset
—————————————————————————————————

Pregeneration traverses each complete region, one by one, and loads/generates terrain gradually. Its goal is to prepare the area without producing noticeable lag spikes.

During pregeneration a margin of \yellow16 chunks per side\reset is added around each region. That margin is only for generation; it does not alter the registered region or the selection CSV.

\yellow/exploration pregen start\reset
Starts pregeneration or resumes saved progress. If the server restarts, the state is preserved and can continue from where it left off.

\yellow/exploration pregen pause\reset
Pauses the work without losing cursor, current region, count or speed. Use it before an event or maintenance if you want to resume afterwards.

\yellow/exploration pregen stop\reset
Stops the work and discards queue progress. Keeps the configured speed, but a new run will start again from the beginning of the regions.

\yellow/exploration pregen status\reset
Shows whether it is active, paused or stopped; current region, maximum speed, performance state and MSPT average.

\yellow/exploration pregen speed <1-1200>\reset
Sets a maximum of chunks per minute. The initial value is 60. It is a ceiling, not a guarantee: the system reduces its pace if the server has less headroom.

\aqua\boldPERFORMANCE PROTECTIONS\reset

Pregeneration does not start working immediately. First it gathers one sample per second for five minutes. To generate it needs a healthy history: average below 20 MSPT, no value above 25 MSPT and a total variation of no more than 6 MSPT.

With the server very comfortable —average below 12 MSPT— it uses up to 100% of the configured speed. Below 16 MSPT it uses up to 50%; between 16 and 20, up to 25%. If conditions stop being healthy, it pauses itself until stability recovers.

It also avoids generating a chunk that is eight chunks or less from a non-spectator player in that dimension. This way it does not compete directly with the area someone is exploring or building in.

When it finishes all regions, it stays automatically paused. You can review Status or Start again if you changed the regions and need to process the new selection.

—————————————————————————————————
\aqua\boldRECOMMENDED ADMIN WORKFLOW\reset
—————————————————————————————————

\dark_gray1. Enable explorationManager and review the map in the correct dimension.
\dark_gray2. Create regions by dragging with right click on the map.
\dark_gray3. Verify that the rectangles cover exactly what you need.
\dark_gray4. Confirm that the automatic CSVs changed before using them in an external tool.
\dark_gray5. Set a sensible pregeneration speed and use Start.
\dark_gray6. Let the system gather its five minutes of samples; do not force load while MSPT is not stable.
\dark_gray7. When finished, decide whether to turn off explorationManager and enable allowPlayerExploration false to turn the regions into a game limit.

Regions, CSVs and pregeneration have related but distinct purposes: region selects, CSV exports and pregeneration prepares. Do not confuse the 16-chunk generation margin with the selection used by world maintenance.
