Turtle Update - *Not Released Yet* - **v0.1.2**
======
## Added Features :  
**/ping** :  
```
Calculate ping and show it
```  
**New god** :
```
Added a new god for continue to follow mc lore
```

## Bug Fix :
**/amper** - *Not Fixed*  
```
Bug has been found for playing amper generated song
Will be corrected as soon as possible
```  
**/soundeffect** - *Not Fixed*  
```
Bug has been found for playing local song
Will be corrected as soon as possible
```  
**Play Queue** - *Fixed*  
```
The queue seems to don't erase finished or skipped song
Bug was linked to vocal timeout in VocalUtilities.py
No more problems
``` 

Turtle Update - *24/04/17* - **v0.1.1**
======

## Added libs :  
**AmperMusicAPI.py** - for using API of AmperMusic https://www.ampermusic.com/

## Added Features :
**/amper** :  
```
/amper descriptors - Show all descirptors available for AmperMusic
/amper descrip time - Generate and play music with AmperMusic
```  

## Bug Fix :
**/showqueue bug** - *Fixed*  
```
Bug on /showqueue when a music not coming from yt was in the queue
```  
**incompatibility with Golem Bot (https://github.com/Indianajaune/Golem)** - *Fixed*  
```
Following commands of golem are generating incompatibilities with Turtle bot :
/player - Corrected
/play - Corrected
/skip - Corrected
```  


Turtle Update - *17/04/17* - **v0.1.0**
======

## Added libs :  
**VocalUtilities.py** - for using vocal commands  
**mojangapi.py** - for using mojang API for minecraft (https://github.com/ttgc/Mojang-API)

## Added Features :  
**/reroll** - **Not released yet**  
```
Allow to reroll someone from Skycraft Minecraft Server
Command does not still work
```  
**/claimprogram**  
```
/claimprogram ID/path - Search programs stored on a turtle or computer of computercraft on Skycraft Minecraft server and show it
if the program is too long the result won't appear
```  
**Vocal commands**  
```
/vocal on|off - Switch on/off the vocal of the bot
/play yt - Play a YT video from url given or search a video and play first result from keywords given
/soundeffect sound - Modo Command - Play a soundeffect from the local directory "Music" of the bot
/showqueue - Show the vocal queue
```  
**Vocal Timeout**  
```
Make the bot timeout and automatically disconnect from vocal when inactiv
Currently set to 1 min
```

## Changed Features :
**/quote**  
```
/quote has been rewritten, need ID to work now, prototyp :
/quote IDmsg [IDchannel] - Search the message with the ID given in the channel with ID given, if IDchannel is not given then the message will be searched into the current channel
```  
**/website**  
```
Changed result of /website :
Before : Only display 'http://skycraft.tech'
Now : Display an Embed redirecting to 'http://skycraft.tech' and give more information about Skycraft
```  
**Other Embed**
```
Embed upgrade, adding author and/or thumbnail field
```  
