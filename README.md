# MetinPythonBot
THIS PROJECT WAS BUILT FOR EDUCATIONAL AND LEARNING PURPOSES ONLY!<br>
This is a long term project built with C++/Python in order to explore my skills as a programmer and reverse engineer.<br>
A Bot/Mod that adds complex functionality to the metin2 client. It needs be used with my c++ python library (eXLib.dll), it will not work without it.<br>

## Functions
- PathFinding (Even across maps)
- WaitDmg (Including bow)
- Pickup (with range)
- SearchBot
- LevelBot (with change location)
- FishBot
- Farmbot
- Skillbot
- Radar
- Mining bot
- Channel Switcher
- Cloud Exploit Damage
- Auto-pot and auto-restart
- Shop-creator
- Inventory Manager
- Teleport
- Auto buy/sell
- SpeedBoost
- AntiExp

## Preview
![image info](https://i.gyazo.com/b1fa500eeaadabc1be91cc7b89782647.jpg)

## Usefull documented helper modules
This are modules built to be integrated with scripts, they provide an interface to complex functionality like walking with pathfinding or creating UI ingame.
All this modules are documented.

- <b>BotBase</b>: Allows to create diferent bot modes while maintaining special features (For now it's only available auto shop).
- <b>FileManager</b>: Allows to store/retrive information from files.
- <b>Movement</b>: Provide movement and teleport functions.
- <b>OpenLib</b>: Main lib containing a lot of helper functions.
- <b>OpenLog</b>: Very simple module for loging informations.
- <b>NPCInteraction</b>: Allows for interaction with NPC's.
- <b>UIComponents</b>: Contains high level functions to draw on UI components.

Try to avoid usage of other modules not referenced here for creating aditional functionality, as other modules are more complex and more prone to error.

## Aditional Remarks
In order to create a new BotMode, you shall extend the BotBase class (see example of LevelBot).
FishingBot do not expand this class because it was made before the creation of BotMode class. 
Every module that needs to keep an Object running in the background like Movement or LevelBot is stored and executed at the end of the file, this allows to easily reload the module at runtime.
The hackbar.py is responsible for importing every Module and showing the initial UI bar.

## FileSystem
Main configurations files, if the files are not mentioned here, it either means they are strictly used by the core bot or they are editable from the UI.

- <b>Resources/Maps:</b>: Contains the maps to be used in pathfinding. If the current map is not available in this directory it will be automatically created. You can edit the map (I recommend using Notepad++, as you can zoom out) the file contains only 0's and 1's, where the 0 represents a blocked location and the 1 represents a walkable position.

- <b>Saves:</b>
Unlike the Maps files, the next specific files are not automatically created and need to be updated, in case a map is not set currently.
- - <b>map_linker.txt</b>: Contains the links between maps, only yhe links contained in this file will be used too look for path across maps.
- - <b>NpcMaps/map_name.npcs</b>: Contains all npc's in that map with the following identation("race x y")

## How to load it
Load eXLib.dll into process while in character select mode or while choosing the channel.

## Notes
- init.py needs to be changed in case the server changes critical modules or functions


# Updates
v1.1:
- Updated to use the latest version of eXLib
- Added SpeedBoost (can be found under settings, general tab)
- Changed installation method (now you are not required to add files to the game folder)
- Now teleports reloads the environment after each teleport
- Minor bug fixes

v2.0:
- Add farmbot (Use this to farm metins or to mine ore)
- Add Skillbot (Using active skills like aura or enchanted blade, is mounting and dismounting horse if needed)
- Add Radar (List of interesting instances around with posibility to warp to them)
- Add AntiExp (Automaticly donate exp do guild)
- Add ChannelSwitcher (Instantly connecting to chosen channel)
- Fix a lot of bugs, crashes are very rare now