# ROLL_BOT

A Discord bot for playing Powered by the Apocalypse RPG engine games easily and remotely. 
The first version of this bot with focus specificly on Dungeon World. Later it be expanded to include mechanics from Apocalypse World, and have more flexiblity to accomodate other games built with the Powered by the Apocalypse engine. 

## Commands
+ $hey - ping the bot make sure it is online
+ $create_char - walks a player through the character creation process and saves the players charactersheet on the backend.
+ $bonds - after players have created their characters use this prompt for each player to fill put bonds. 
+ $read_sheet - prints the player's character-sheet into the discord chat.
+ $read_bonds - prints the player's bonds into the discord chat. 
+ $view_items - prints the player's inventory into the discord chat. 
+ $delete_character - confirms if you are sure and then deletes players character sheet.
+ $lvl_up - allows a player to update their character sheet
+ $roll - roll dice function use _d_ syntax ex: "/roll 2d6" this will roll two six sided dice and print the output into the chat.
+ $roll _d_ + attr - roll function that follows the same syntax as above but also include the value of characters stats. ex: "/roll 2d6 + dexterity" will roll two six sided dice plus the players dexterity modifier. 
+ $damage - roll your characters damage plus any additional die. 
+ 

## Planned Changes
  + Fix $lvl_up function 
  + Add inventory for all Classes
  + figure out way to deal with class specific moves and advanced moves
  + $command functions for all basic moves shared by all players
  + appoint player to be Game Master and have set of moves specifc to them.  
