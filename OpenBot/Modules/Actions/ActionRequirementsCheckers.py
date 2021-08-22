from OpenBot.Modules import OpenLib
from OpenBot.Modules.OpenLog import DebugPrint
import eXLib
import player, background, chat, chr, net

# REQUIREMENTS
IS_NEAR_POSITION = 'IS_NEAR_POSITION'
IS_ON_POSITION = 'IS_ON_POSITION'
IS_IN_MAP = 'IS_IN_MAP'
IS_ABOVE_LVL = 'IS_ABOVE_LVL'
IS_NEAR_INSTANCE = 'IS_NEAR_INSTANCE'
IS_RACE_NEARLY = 'IS_RACE_NEARLY'
IS_IN_CHANNEL = 'IS_IN_CHANNEL'

req_list = [IS_NEAR_POSITION, IS_ON_POSITION, IS_IN_MAP, IS_ABOVE_LVL, IS_NEAR_INSTANCE, IS_RACE_NEARLY, IS_IN_CHANNEL]

def isAboveLVL(lvl):
    """
     Checking is main character above level
        Args:
            lvl (int)

    """
    
    
    if player.GetStatus(player.LEVEL) < lvl:
        return False
    return True

def isInMaps(maps):
    """
        Checking is main character on any of map in list
        Args:
            maps ['map_name_1' (str), 'map_name_2' (str)] (list)

    """
    for mapName in maps:
        if str(background.GetCurrentMapName()) == mapName:
            return True
    return False

def isNearInstance(vid):
    return OpenLib.isPlayerCloseToInstance(vid)

def isNearPosition(position):
    """
        Checking is main character near position.
        Args:
            position [x (int), y(int), max_dist(int)](list)

    """
    x, y = position[0], position[1]
    if len(position) < 3:
        max_dist = 100
    else:
        max_dist = position[2]
    return OpenLib.isPlayerCloseToPosition(x, y, max_dist)

def isOnPosition(position):
    """
        Checking is main character on current position.
        Args:
            position [x (int), y(int), max_dist(int)](list)

    """
    x, y = position[0], position[1]
    if len(position) < 3:
        max_dist = 100
    else:
        max_dist = position[2]
    if OpenLib.isPlayerCloseToPosition(x, y, max_dist):
        return True
    return False

def isMetinNearly(args=0):
    for vid in eXLib.InstancesList:
        if OpenLib.IsThisMetin(vid) and not eXLib.IsDead(vid):
            if not OpenLib.isPathToVID(vid):
                continue
            return True
    return False

def isOreNearly(args=0):
    for vid in eXLib.InstancesList:
        if OpenLib.IsThisOre(vid) and not eXLib.IsDead(vid):
            if not OpenLib.isPathToVID(vid):
                continue
            return True
    return False

def isRaceNearly(races_list):
    for vid in eXLib.InstancesList:
        chr.SelectInstance(vid)
        if chr.GetRace() in races_list:
            return True
    return False

def isCharReadyToMine(ore_vid):

    if eXLib.IsDead(ore_vid):
        return False

    if not OpenLib.isPlayerCloseToInstance(ore_vid):
        return False
    
    if not OpenLib.IsWeaponPickaxe():
        return False

    return True

def HasItem(item_id):
    if OpenLib.GetItemByID(item_id) > -1:
        return True
    return False

def IsDead(vid):
    return eXLib.IsDead(vid)

def IsInChannel(channel):
    if OpenLib.GetCurrentChannel() == channel:
        return True
    return False