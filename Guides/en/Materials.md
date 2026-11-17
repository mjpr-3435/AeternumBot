\gold\boldMATERIALS: PROJECT COLLECTION LISTS\reset

The materials system tracks the items a project needs and how many are still missing. It compares the target amounts against what is stored in a single storage area and what each player is carrying.

Administration activates \yellowcommandMaterials\reset to enable \yellow/materials\reset. The interface requires the Aeternum Carpet client.

—————————————————————————————————
\aqua\boldHOW LISTS ARE BUILT\reset
—————————————————————————————————

Each list is a CSV file inside \yellowworld/data/aeternum_materials/\reset. The file name becomes the list title. Columns:

\dark_gray• \whiteItem\reset: display name of the item (for example "White Wool").
\dark_gray• \whiteTotal\reset: how many of that item the project needs.
\dark_gray• \whiteMissing\reset and \whiteAvailable\reset: informational. The real available count comes from the storage scan, not from the CSV.

\yellow/materials\reset — \greenFOR EVERYONE\reset
Opens the list panel. Choose a list to open its detail screen with Item, Total, Missing and Claim columns.

—————————————————————————————————
\aqua\boldSTORAGE: ONE AREA PER LIST\reset
—————————————————————————————————

Each list has a single storage area. The server scans it every second and updates how many items are available.

\yellow/materials storage add <list> <coord1> <coord2>\reset — \redOP ONLY\reset
Assigns the storage area of a list. If the list already has one, the command is rejected: remove the existing area before assigning another.

\yellow/materials storage list\reset — \redOP ONLY\reset
Shows the assigned storage areas with a clickable X to remove one.

\yellow/materials storage del <list> <index>\reset — \redOP ONLY\reset
Removes the indicated storage area.

—————————————————————————————————
\aqua\boldCLAIMS\reset
—————————————————————————————————

Each player can claim an item in a list with its Claim button to take responsibility for farming it. The detail screen shows who claimed each item; only the claimant can unclaim it.

—————————————————————————————————
\aqua\boldLIST ORDER\reset
—————————————————————————————————

The detail screen shows two groups:

\dark_gray1. Missing items first (available below the target), sorted by total from largest to smallest.
\dark_gray2. Already completed items (available at or above the target), also sorted by total from largest to smallest.

—————————————————————————————————
\aqua\boldHUD OVERLAY\reset
—————————————————————————————————

While playing, the overlay on the right shows your claimed items that are still missing, sorted by total from largest to smallest. The count is calculated on the server and considers both the storage area and what you carry in your inventory, including shulker contents and shulkers inside shulkers.

This lets you collect without depositing constantly: the missing value drops as you carry the items, and once storage plus inventory covers the target, the item leaves the overlay. The overlay is personal, refreshes from the server and clears automatically when you change worlds or reconnect.

—————————————————————————————————
\aqua\boldQUANTITY FORMAT\reset
—————————————————————————————————

Amounts are shown in progressive units:

\dark_gray• Loose items: the number directly.
\dark_gray• Stacks: \yellow64 x N + Y\reset.
\dark_gray• \yellowSB\reset (Shulker Box): above 1,728 items, counted in shulkers of 1,728.
\dark_gray• \yellowSDC\reset (Shulker Double Chest): above 93,312 items, counted in double chests of shulker boxes (54 shulkers each).

\dark_grayExample: 93,312 items = 1 SDC = 54 shulkers.
