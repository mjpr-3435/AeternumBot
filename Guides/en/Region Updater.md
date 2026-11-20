\gold\boldREGION UPDATER\reset

The updater exists on the creative servers, not on SMP Survival. It copies real regions from SMP to CMP, MMP or PMP to work with the terrain, builds and original context without touching Survival or using creative there.

—————————————————————————————————
\aqua\boldSELECTING\reset
—————————————————————————————————

\yellow!!ru add\reset
Marks the current region to copy it from SMP to the current creative server.

\yellow!!ru pos1\reset and \yellow!!ru pos2\reset
Mark two corners in the same dimension to add all regions inside that rectangle to the copy list.

\yellow!!rm add\reset
Marks the current region to remove it from the current creative server.

\yellow!!rm pos1\reset and \yellow!!rm pos2\reset
Mark two corners in the same dimension to add all regions inside that rectangle to the removal list.

\yellow!!ru list\reset
Shows the list: \greenru\reset means copy from SMP and \redrm\reset means remove from the destination.

\yellow!!ru clear\reset
Empties both lists and clears any pending \yellowpos1\reset / \yellowpos2\reset corners.

\dark_grayEach region measures 512 × 512 blocks. It includes a complete Overworld, Nether or End region depending on where you are; it is not a fine selection. Selections are capped at \yellow2,500 regions\reset (approx. 25.6k × 25.6k blocks).

—————————————————————————————————
\aqua\boldUPDATING THE CREATIVE SERVER\reset
—————————————————————————————————

\yellow!!ru update\reset
Applies the current list. It is available to anyone who can use the creative server; does not require administrator permissions.

The system warns everyone, waits 5 seconds, saves SMP if it is running, stops the destination server, applies changes and starts it again.

When copying, terrain, entities and POI data are transferred together. SMP is only the source: this command never modifies the original SMP region.

\red\boldThere is no additional confirmation. Use !!ru list just before updating.\reset Destination players will be kicked during the restart.

\red\boldDeleting with !!rm add or !!rm pos1/pos2 has no recycle bin.\reset If the destination contains work you want to keep, first create a regional backup.
