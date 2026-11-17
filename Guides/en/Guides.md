\gold\boldSERVER GUIDES\reset

Guides are the help library visible within Minecraft. They allow players and administrators to look up server procedures without relying on Discord, local files or another person online.

The server is the source of truth. Guides live as files in language subdirectories: \yellowworld/data/aeternum_guides/es/\reset and \yellowworld/data/aeternum_guides/en/\reset. They are sent to the client when opening the library. To use the interface, both client and server need Aeternum Carpet.

To enable it, administration activates the \yellowcommandGuide\reset rule.

—————————————————————————————————
\green\boldFOR EVERYONE: READING GUIDES\reset
—————————————————————————————————

\yellow/guide\reset
Opens your personal guide library in Spanish. It does not modify anything or notify other players.

The \yellow[ES]\reset and \yellow[EN]\reset buttons in the upper corner switch between the Spanish and English guides. Each language has its own independent set of guides, order and files. The tooltip of each button is in its own language.

The left column contains the titles. Click on one to read it on the right. If there are too many titles, use the scroll wheel over that column; long titles are visually clipped to stay within the panel, but their content is not lost.

A guide's text can be longer than the visible area. Use the scroll wheel over the text or drag the vertical bar on the right. Line breaks are respected: an empty line in the file creates a gap in the reader.

Only OPs see the \yellowEdit\reset and \yellowRefresh\reset buttons. A normal player can only read, switch languages and close the library.

—————————————————————————————————
\red\boldADMINISTRATION ONLY: EDITING\reset
—————————————————————————————————

Select a guide and press \yellowEdit\reset. The button changes to \yellowGuides\reset to clearly return to the reader without closing the entire panel. Escape also goes back from the editor to the reader; from the reader it closes the library.

Edits are saved in the active language subdirectory. If you are viewing guides in Spanish, changes go to \yellowes/\reset. Switch languages with the upper buttons to edit the other set.

\aqua\boldCONTENT AND AUTO-SAVE\reset

Write directly in the editor's large area. There is no Save button: moments after you stop typing, the status changes from \yellowSaving...\reset to \greenSaved\reset and the server writes the file.

Do not close the game while \yellowSaving...\reset is displayed. Wait for it to show \greenSaved\reset to confirm the last change reached the server.

Each guide can contain up to 100,000 characters. The editor preserves line breaks and allows scrolling through long texts.

\aqua\boldCREATING\reset

The \yellow+\reset button creates a new guide in the current language. The server starts from \whiteNew guide\reset; if it already exists, it creates \whiteNew guide 2\reset, \whiteNew guide 3\reset and so on. Then write the final title and content.

\aqua\boldRENAMING\reset

Above the content is the title field. The ✓ button stays off while the title is the same. When you type a different and valid title it lights up; click it to confirm the change.

The title is also the filename. It must be unique and can be between 1 and 64 characters: unaccented letters, numbers, spaces, \white_\reset and \white-\reset. Do not use /, \#, accents, punctuation marks or other special characters.

Renaming changes the file \white<Title>.md\reset. If a guide with the chosen title already exists, the change is rejected to avoid overwriting it.

\aqua\boldORDERING\reset

In the editor, each row in the guide list shows two arrows: ▲ to move up one position and ▼ to move down. The order is saved in \yellow.aeternum_guide_order\reset inside the corresponding language folder.

\aqua\boldDELETING\reset

The X button deletes the selected guide and its file. You must hold \yellowShift\reset to activate it. There is no recycle bin or additional confirmation: before deleting an important guide, copy it or verify it is in version control.

—————————————————————————————————
\aqua\boldTEXT FORMATTING\reset
—————————————————————————————————

Although the files use the \white.md\reset extension, the reader does not render Markdown or HTML. For example, \white# title\reset, \white**bold**\reset and Markdown links will be displayed as plain text.

Use the same color and style format as the welcome banner. Write a backslash followed by the color or style name just before the text you want to affect. To return to normal style, write a backslash followed by \whitereset\reset.

\aqua\boldCOLORS\reset

\whiteblack — black · dark_blue — dark blue · dark_green — dark green
dark_aqua — dark aqua · dark_red — dark red · dark_purple — dark purple
gold — gold · gray — gray · dark_gray — dark gray · blue — blue
green — green · aqua — aqua · red — red · light_purple — light purple
yellow — yellow · white — white

\aqua\boldSTYLES\reset

\whitebold\reset — bold
\whiteitalic\reset — italic
\whiteunderline\reset — underline
\whitestrikethrough\reset — strikethrough
\whiteobfuscated\reset — obfuscated text
\whitereset\reset — returns to normal color and style

\dark_grayConceptual example: write backslash followed by aqua and bold before a heading; write backslash followed by reset when done. For a warning, write backslash followed by red and bold before "Attention", and reset afterwards.

The ? button in the editor shows a cheat sheet with the available codes. Use it if you don't remember the syntax while typing.

—————————————————————————————————
\red\boldRELOAD SERVER FILES\reset
—————————————————————————————————

\yellowRefresh\reset — \redOP ONLY\reset
Re-reads the guide folder for the current language. Detects files added, edited, renamed or deleted outside the game and syncs the library of connected players viewing that same language.

Use it after copying a new guide, updating files from a repository or modifying text with an external editor. No server restart is needed.

When reloading, only \white.md\reset files whose name is a valid title are considered. A file with forbidden characters in the name is ignored until renamed correctly.

If you edit an external file while someone has their guide open in the editor with pending changes, that client temporarily keeps their edit to avoid overwriting it. Wait for them to save or ask the person to exit the editor before a major reload.

—————————————————————————————————
\aqua\boldRECOMMENDED WORKFLOW\reset
—————————————————————————————————

\dark_gray1. Create or select a guide from /guide.
\dark_gray2. Write the title and content; check that Saved appears.
\dark_gray3. Use ? to check colors and styles.
\dark_gray4. Return to Guides, read it as a player and verify line breaks and scrolling.
\dark_gray5. Order the guide with ▲ and ▼ in the list if needed.
\dark_gray6. If the change came from external files, press Refresh.

Keep titles short and clear. The library works best when each guide answers a specific need and Commands.md links to the corresponding detailed guide.
