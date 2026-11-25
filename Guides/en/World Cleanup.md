\gold\boldWORLD CLEANUP\reset

Cleanup removes chunks outside the allowed exploration areas. The CSVs exported by AeternumCarpet are the source of truth: selected chunks are preserved and the rest can be deleted.

\red\boldCONFIGURED OPERATOR ONLY\reset

This tool is restricted by configuration: only the player set in \yellowWorldTrimmer.Operator\reset (in \yellowconfig.yml\reset / \yellow/config\reset) can prepare or confirm a trim. Being an administrator is not enough.

\dark_grayThe reason is simple: it is a destructive operation with no recycle bin, so it is reserved for the designated operator managing the exploration, CSV and cleanup workflow.

\yellow!!trim\reset
Prepares a cleanup. Checks the Overworld, Nether and End CSVs and shows how many chunks will be preserved. Preparing does not delete anything.

\yellow!!trim confirm\reset
Confirms the prepared cleanup. Must be confirmed by the same configured operator who prepared it.

—————————————————————————————————
\red\boldBEFORE CONFIRMING\reset
—————————————————————————————————

1. Review exploration areas and their export in AeternumCarpet.
2. Make an independent general backup.
3. Run !!trim and verify the numbers shown.
4. Confirm only if that selection represents exactly what should survive.

\dark_grayNo radius or hidden margin is added: exactly what is indicated by the CSVs is preserved. If more terrain is needed, areas are expanded before preparing.

If a dimension has stored chunks but its preservation CSV is empty, it is cancelled for safety rather than emptied.

During the operation the server is stopped. Region data, POI and entities outside the selection are deleted, and the server restarts even if an error occurred.

\red\boldThe tool does not create its own backup.\reset On first use it may download and verify MCA Selector; the result appears in the process console.
