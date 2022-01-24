_chr = chr
from OpenBot.Modules.Hooks import Hook, questHook
import Hooks, Data
import ui,chr,time,app, net, background, player,wndMgr,math,snd,eXLib,uiToolTip,item,FileManager,event,chat,OpenLog,skill, m2netm2g
from datetime import datetime
#import pack

#Range of player attack
ATTACK_RANGE = 270

#Types
NONE_TYPE = -99
OBJECT_TYPE = 1
METIN_TYPE = 2
MONSTER_TYPE = 0
PLAYER_TYPE = 6
BOSS_TYPE = -1
ORE_TYPE = -2

BOSS_IDS = dict()
ORES_IDS = dict()
#SEARCH_ITEMS_MAX_PRICE = dict()

WARRIOR_MALE_ID = 1
WARRIOR_FEMALE_ID = 4
SURA_MALE_ID = 2
SURA_FEMALE_ID = 6
NINJA_MALE_ID = 1
NINJA_FEMALE_ID = 5
SHAMAN_MALE_ID = 3
SHAMAN_FEMALE_ID = 7

MAX_INVENTORY_SIZE = 90

# Max teleport distance before resync by server
MAX_TELEPORT_DIST = 2400
ATTACK_MAX_DIST_NO_TELEPORT = 290

MIN_RACE_SHOP = 30000
MAX_RACE_SHOP = 30008

#Possible game phases
PHASE_LOGIN = 1
PHASE_SELECT = 2
PHASE_GAME = 5


#Minumum number of empty slots for the inventory to be considered full
INV_FULL_MIN_EMPTY = 10
MAX_ITEM_COUNT = 200

#Maximum distance to pickup before telport
MAX_PICKUP_DIST = 290.0


#State of a player
MOVING_TO_TARGET = 1
ATTACKING_TARGET = 0
TARGET_IS_DEAD = -1

#SkillSet
SKILL_SET_NONE = 0
SKILL_SET_BODY_WARRIOR = 1
SKILL_SET_MENTAL_WARRIOR = 2
SKILL_SET_DAGGER_NINJA = 3
SKILL_SET_ARCHER_NINJA = 4
SKILL_SET_WEAPONS_SURA = 5
SKILL_SET_MAGIC_SURA = 6
SKILL_SET_DRAGON_SHAMAN = 7
SKILL_SET_HEAL_SHAMAN = 8
SKILL_SET_1_LYCAN = 9

skillSet_map = {
	SKILL_SET_NONE : ["NONE",0],
	SKILL_SET_BODY_WARRIOR : ["warrior",1],
	SKILL_SET_MENTAL_WARRIOR : ["warrior",16],
	SKILL_SET_DAGGER_NINJA : ["assassin",31],
	SKILL_SET_ARCHER_NINJA : ["assassin",46],
	SKILL_SET_WEAPONS_SURA : ["sura",61],
	SKILL_SET_MAGIC_SURA : ["sura",76],
	SKILL_SET_DRAGON_SHAMAN : ["shaman",91],
	SKILL_SET_HEAL_SHAMAN : ["shaman",106],
	SKILL_SET_1_LYCAN : ["wolfman",170]
}

#Contains the following information about the skills
#"CLASS"
#"NAME"
#"ICON"
SKILL_INFORMATION = FileManager.parseSkillDesc()

def Revive(in_city=False):
	"""
	Revive the main instance.
	"""
	player.SetAttackKeyState(False)
	if not in_city:
		net.SendCommandPacket(m2netm2g.PLAYER_CMD_RESTART, 1)
	else:
		net.SendCommandPacket(m2netm2g.PLAYER_CMD_REVIVE, 1)

def ConvertPrice(price_str,item_num=1):
	"""
	Converts the string price.
	Given the price in "kk" the function will return the price in wons and yang.
	Example: "435kk" -> 4, 35000000
	Args:
		price_str ([type]): [description]
		item_num (int, optional): [description]. Defaults to 1.

	Returns:
		[(int,int)]: Tupple containing the number of wons and the amount of yang respectivly. 
	"""
	multiplier = price_str.count("k")	
	yang = float(price_str.replace("k",""))
	yang *= 1000**multiplier
	yang  *= item_num

	wons = int(yang/100000000)
	if(wons > 0):
		rest_yang = int(yang % (wons*100000000))
	else:
		rest_yang = int(yang)

	return (wons,rest_yang)

def GetSkillIconPath(id,grade=3):
	"""
	Returns the icon path of a skill image.
	Args:
		id(int) : Id of the skill.
		grade(int) : Grade of the skill 1-3.
	"""
	skill = SKILL_INFORMATION[id]
	skill_class = skill["class"]
	skill_icon_name = skill["icon"]
	return "d:/ymir work/ui/skill/" + skill_class + "/" + skill_icon_name + "_0"+str(grade)+".sub"

def GetClassSkillIDs(_class):
	"""
	Returns all skill ids of each class.
	Args:
		_class(int) : The SkillSet of the class.
	"""
	startIndex = skillSet_map[_class][1]
	return [ i for i in range(skillSet_map[_class][1],startIndex+6)]

def GetServerInfo(channel):
	"""
	Returns the channel info
	"""
	import serverInfo, Data
	for serverNum in serverInfo.REGION_DICT[0].keys():
		if serverInfo.REGION_DICT[0][serverNum]['name'] == Data.serverInfo.split(',')[0]:
			serverName = serverInfo.REGION_DICT[0][serverNum]['name']
			channelName = serverInfo.REGION_DICT[0][serverNum]['channel'][channel]['name']
			account_addr_new = serverInfo.REGION_AUTH_SERVER_DICT[0][serverNum]['ip']
			account_port_new = serverInfo.REGION_AUTH_SERVER_DICT[0][serverNum]['port']
			addr_new = serverInfo.REGION_DICT[0][serverNum]['channel'][channel]['ip']
			port_new = serverInfo.REGION_DICT[0][serverNum]['channel'][channel]['tcp_port']
			return (serverName,
	         channelName,
	         account_addr_new,
	         account_port_new,
	         addr_new,
	         port_new)

def GetClass():
	"""
	Returns the a distinct number associated with the skillgroup
	The possible values are on the beginning of this file under skillset

	Returns:
		[(int,int)]: Returns a distinct number ofr each skill group or SKILL_SET_NONE if player has no skillset. 
	"""
	race = Data.mainRace
	group = Data.mainSkillGroup

	race = race % 4
	if(group!= 0):
		return (2*race)+group
	
	return 0
		
#Skip python select answers
def skipAnswers(event_answers, hook=False):
	"""
	Selects the event to be answers.
	if hook=True will avoid quest answers from showing on screen, the caller is then resposible for removing the hook afterwards by calling showAnswers.

	Args:
		event_answers ([list]): A list containing the index of the answers.
		hook ([boolean]): If true will hook quest answers, in order to not show it on screen.
	"""
	if hook:
		questHook.HookFunction()
	for index,answer in enumerate(event_answers,start=1):
		event.SelectAnswer(index,answer)

def showAnswers():
	"""
	Removes the quest hook, in order for quest answers to be displayed.
	"""
	Hooks.questHook.UnhookFunction()

def GetCurrentText(self):
	return self.textLine.GetText()

def GetSkillManaNeed(skill_id,skill_slot):
	return skill.GetSkillNeedSP(skill_id,player.GetSkillCurrentEfficientPercentage(skill_slot))

def OnSelectItem(self, index, name):
	self.SetCurrentItem(name)
	self.CloseListBox()
	self.event()
	
def GetSelectedIndex(self):
	return self.listBox.GetSelectedItem()

def IsThisNPC(vid):
	if chr.GetInstanceType(vid) == OBJECT_TYPE:
		return True
	return False

def IsThisPlayer(vid):
	if chr.GetInstanceType(vid) == PLAYER_TYPE:
		return True
	return False

def IsAnyPlayerHere():
	for vid in eXLib.InstancesList:
		if Data.mainVID != vid:
			if IsThisPlayer(vid):
				return True
	return False

def IsThisMetin(vid):
	if chr.GetInstanceType(vid) == METIN_TYPE:
		return True
	return False

def IsThisBoss(vid):
	"""
	Check if instance is boss.

	Args:
		vnum ([int]): Virtual number of the instance.

	Returns:
		[bool]: Returns True if is boss and False otherwise.
	"""
	chr.SelectInstance(vid)
	if chr.GetRace() in BOSS_IDS.keys():
		return True
	return False

def IsThisOre(vid):
	chr.SelectInstance(vid)
	if chr.GetRace() in ORES_IDS.keys():
		return True
	return False

#Checks if inventory is full by checking empty spaces
def isInventoryFull():
	global player
	INV_FULL_MIN_EMPTY = 10
	MAX_INVENTORY_SIZE = 90
	"""
	Check if invetory is full.
	The invtory is considered full when the number of empty slots is smaller then INV_FULL_MIN_EMPTY.

	Returns:
		[bool]: Returns True if is full or False otherwise.
	"""
	numItems = MAX_INVENTORY_SIZE
	for i in range(0,MAX_INVENTORY_SIZE):
		curr_id = player.GetItemIndex(i)
		if curr_id != 0:
			item.SelectItem(curr_id)
			s = item.GetItemSize()
			numItems-=s[0]*s[1]
	
	if numItems < INV_FULL_MIN_EMPTY:
		return True
	else:
		return False

def GetNumberOfFreeSlots():
	global player
	INV_FULL_MIN_EMPTY = 10
	MAX_INVENTORY_SIZE = 90
	numItems = MAX_INVENTORY_SIZE
	for i in range(0,MAX_INVENTORY_SIZE):
		curr_id = player.GetItemIndex(i)
		if curr_id != 0:
			item.SelectItem(curr_id)
			s = item.GetItemSize()
			numItems-=s[0]*s[1]
	
	if numItems < INV_FULL_MIN_EMPTY:
		return 0
	else:
		return numItems - INV_FULL_MIN_EMPTY

def GetItemByType(_id):
	"""
	Return the slot index of the first item with the specified type in the inventory.

	Args:
		_id ([int]): The type of the item.

	Returns:
		[int]: Returns the slot index that matches the type or returns -1 if it is not found.  
	"""
	for i in range(0,MAX_INVENTORY_SIZE):
		curr_id = player.GetItemIndex(i)
		if curr_id == 0:
			continue
		item.SelectItem(curr_id)
		if item.GetItemType() == _id:
			return i
	return -1

def UseAnyItemByID(id_list):
	"""
	Use the first item found that matches any of the id specified.

	Args:
		id_list ([list]): List of item ids.

	Returns:
		[int]: Returns 1 if the item was used or -1 otherwise.
	"""
	for i in range(0,MAX_INVENTORY_SIZE):
		if player.GetItemIndex(i) in id_list:
			net.SendItemUsePacket(i)
			return 1
	return -1

def GetItemByID(_id):
	"""
	Returns the index slot of first item found that matches any of the item id specified in the inventory.

	Args:
		id_list ([list]): List of item ids.

	Returns:
		[int]: Returns the index of the item or -1 if the item doesn't exist in the inventory.
	"""
	for i in range(0,MAX_INVENTORY_SIZE):
		if player.GetItemIndex(i) == _id:
			return i
	return -1

def isItemTypeOnSlot(_type,invType = player.EQUIPMENT,slot=item.EQUIPMENT_WEAPON):
	"""
	Check if a specified item type exists in a specified slot.

	Args:
		_type ([int]): The item type.
		invType ([int], optional): The inventory type. Defaults to player.EQUIPMENT.
		slot ([type], optional): The slot number. Defaults to item.EQUIPMENT_WEAPON.

	Returns:
		[bool]: Returns True if item exist with the specified type or False otherwise.
	"""
	idx = player.GetItemIndex(invType,slot)
	if idx != 0:
		item.SelectItem(idx)
		if item.GetItemType() == _type:
			return True
	return False

#returns a dicitionary containing the positions of each id in _id_list
def GetItemsSlotsByID(_id_list):
	"""
	Return a dictionary containing the slots positions of each id in _id_list.

	Args:
		_id_list ([list]): List with item ids.

	Returns:
		[dict]: Return a dictionary containing the slots positions mapped to a list of slot positions.
	"""
	result = {_id : [] for _id in _id_list}
	for i in range(0,MAX_INVENTORY_SIZE):
		id = player.GetItemIndex(i)
		if player.GetItemIndex(i) in _id_list:
			result[id].append(i)
	return result

#Return the angle needed to rotate from x0,y0 to x1,y1
def GetRotation(x0,y0,x1,y1):
	"""
	Calculate the rotation for (x0,y0) be pointing to (x1,y1), in the game context.

	Args:
		x0 ([float]): X of point a.
		y0 ([float]): Y of point a.
		x1 ([float]): X of point b.
		y1 ([float]): Y of point b.

	Returns:
		[float]: Returns the rotation needed in the game context.
	"""
	x1_relative = x1-x0
	y1_relative = y1-y0
	try:
		rada = 180 * (math.acos(y1_relative/math.sqrt((x1_relative)**2 + (y1_relative)**2))) / math.pi + 180
		if x0 >= x1:
			rada = 360 - rada
	except:
		rada = 0
	return rada

#Rotate Main Character to  x,y
def RotateMainCharacter(x,y):
	"""
	Rotate main character to (x,y)

	Args:
		x ([float]): X coordinate of destination.
		y ([float]): Y coordinate of destination.
	"""
	my_x,my_y,my_z = player.GetMainCharacterPosition()
	chr.SelectInstance(player.GetMainCharacterIndex())
	rot = GetRotation(my_x,my_y,x,y)
	chr.SetRotation(rot)

def RotateMainCharacterByVid(vid):
	chr.SelectInstance(vid)
	x, y, z = chr.GetPixelPosition()
	RotateMainCharacter(x, y)

def GetCurrentPhase():
	"""
	Returns the current phase of the game.

	Returns:
		[int]: Return the current phase of the game.
	"""
	#return eXLib.GetCurrentPhase()
	return Hooks.GetCurrentPhase()

def IsMonsterNearby():
	for vid in eXLib.InstancesList:
		if vid != player.GetMainCharacterIndex():
			_type = chr.GetInstanceType(vid)
			if _type == MONSTER_TYPE or _type == METIN_TYPE:
				return True
	return False

def IsInGamePhase():
	"""
	Check if is in game phase.

	Returns:
		[bool]: Returns True if is in game phase or False otherwise.
	"""
	return GetCurrentPhase() == PHASE_GAME

def getAllStatusOfMainActor():
	"""
	Returns the currents stats of main character.

	Returns:
		dict

	"""
	x, y, z = chr.GetPixelPosition(Data.mainVID)
	character_status = {
		'Position': [x, y],
		'CurrentMap': background.GetCurrentMapName(),
		'Name': player.GetName(),
		'Level': player.GetStatus(player.LEVEL),
		'Experience': player.GetEXP(),
		'MaxExperience': player.GetStatus(player.NEXT_EXP),
		'FirstEmpireMap': GetPlayerEmpireFirstMap(),
		'SecondEmpireMap': GetPlayerEmpireSecondMap(),
		'Money': player.GetMoney(),
		'MovingSpeed': player.GetStatus(player.MOVING_SPEED),
		'GUILD_ID': player.GetGuildID(),
		'GuildName': player.GetGuildName(),
		'DefBonus': player.GetStatus(player.DEF_BONUS),
		'AttBonus': player.GetStatus(player.ATT_BONUS),
		'AttPower': player.GetStatus(player.ATT_POWER),
		'AttSpeed': player.GetStatus(player.ATT_SPEED),
		'MaxHP': player.GetStatus(player.MAX_HP),
		'HP': player.GetStatus(player.HP),
		'RecoveryHP': player.GetStatus(player.HP_RECOVERY),
		'MaxSP': player.GetStatus(player.MAX_SP),
		'SP': player.GetStatus(player.SP),
		'RecoverySP': player.GetStatus(player.SP_RECOVERY),
		'Stamina': player.GetStatus(player.STAMINA),
		#'STAT': player.GetStatus()player.STAT

	}

	return character_status

def GetNearestMonsterVid():
	(closest_vid,_dist) = (0,999999999)
	my_pos = player.GetMainCharacterPosition()
	for vid in eXLib.InstancesList:
		if not chr.HasInstance(vid):
			continue

		if eXLib.IsDead(vid):
			continue
		
		_type = chr.GetInstanceType(vid)
		if MONSTER_TYPE == _type or METIN_TYPE == _type:
			monst_pos = chr.GetPixelPosition(vid)
			this_dist = dist(my_pos[0],my_pos[1],monst_pos[0],monst_pos[1])

			if this_dist < _dist:
				_dist = this_dist
				closest_vid = vid
		
	return closest_vid

def isPathToVID(vid_target):
	x, y, z = chr.GetPixelPosition(vid_target)
	my_x, my_y, my_z = chr.GetPixelPosition(Data.mainVID)
	if eXLib.FindPath(my_x, my_y, x, y):
		return True
	return False

def isPlayerCloseToInstance(vid_target, max_dist=150):
	"""
	Check if an instance is close to another instance.

	Args:
		vid_target ([type]): [description]

	Returns:
		[type]: [description]
	"""
	if vid_target not in eXLib.InstancesList:
		return False

	player_x, player_y, player_z = player.GetMainCharacterPosition()
	target_x, target_y, target_z = chr.GetPixelPosition(vid_target)
	distance = dist(target_x, target_y, player_x, player_y)

	if distance < max_dist:
		return True
	
	return False

def isPlayerCloseToPosition(position_x, position_y, max_dist=150):
	player_x, player_y, player_z = player.GetMainCharacterPosition()
	distance = dist(position_x, position_y, player_x, player_y)

	if distance < max_dist:
		return True
	
	return False

def GetInstanceByID(_id):
	for vid in eXLib.InstancesList:
		if not chr.HasInstance(vid):
			continue
		if eXLib.IsDead(vid):
			continue
		mob_x,mob_y,mob_z = chr.GetPixelPosition(vid)
		if eXLib.IsPositionBlocked(mob_x,mob_y):
			continue
		chr.SelectInstance(vid)
		if chr.GetRace() == _id:
			return vid
	return -1
	
def getClosestInstance(_type,is_unblocked=True):
	"""
	Get the VID of the closest matching one of the types specified instance from the main player.

	Args:
		_type ([list]): A list of VID types.
		is_unblocked (bool, optional): If True it will ignore instance in walls. Defaults to True.

	Returns:
		[int]: Returns the VID of the closest instance.
	"""
	(closest_vid,_dist) = (-1,999999999)
	for vid in eXLib.InstancesList:
		if not chr.HasInstance(vid):
			continue

		if is_unblocked:
			mob_x,mob_y,mob_z = chr.GetPixelPosition(vid)
			if eXLib.IsPositionBlocked(mob_x,mob_y):
				continue

		this_distance = player.GetCharacterDistance(vid)
		if eXLib.IsDead(vid):
			continue

		type = chr.GetInstanceType(vid)
		if type in _type:
			if this_distance < _dist and not isPlayerCloseToInstance(vid):
				_dist = this_distance
				closest_vid = vid
	
	return closest_vid

#Retuns -1 if is dead, 0 if attacking target or 1 if moving to target
def AttackTarget(vid):
	"""
	Attack the instance vid.
	If the player is not in range, it will start an action to move to the target.
	Args:
		vid ([int]): The target VID.

	Returns:
		[int]: If the target is dead returns TARGET_IS_DEAD, if is attacking the target returns ATTACKING_TARGET else returns MOVING_TO_TARGET
	"""
	if eXLib.IsDead(vid):
		return TARGET_IS_DEAD
	mob_x,mob_y,mob_z = chr.GetPixelPosition(vid)
	if player.GetCharacterDistance(vid) < ATTACK_RANGE:
		Movement.StopMovement()
		RotateMainCharacter(mob_x,mob_y)
		player.SetAttackKeyState(True)
		return ATTACKING_TARGET
	else:
		player.SetAttackKeyState(False)
		Movement.GoToPositionAvoidingObjects(mob_x,mob_y)
		return MOVING_TO_TARGET
		
#Return point between 2 points at the specified distance from x1,y1
#If overflow=False and dist_ is bigger then the distance between the 2 points
#the function will return x2,y2, otherwise it will return a point beyond x2,y2
def getPointsDistance(x1,y1,x2,y2,dist_,allow_overflow=False):
	"""
	Return a point between 2 points at the specified distance from x1,y1.
	If overflow=False and dist_ is bigger then the distance between the 2 points the function will return x2,y2, otherwise it will return a point beyond x2,y2.

	Args:
		x1 ([float]): X1
		y1 ([float]): Y1
		x2 ([float]): X2
		y2 ([float]): Y2
		dist_ ([float]): The distance from the point 1.
		allow_overflow (bool, optional): If allows overflow or not. Defaults to False.

	Returns:
		[Tupple]: Returns a tupple containing the specified point (x,y)
	"""
	d = dist(x1,y1,x2,y2)
	if(d < 0.0001):
		return(x1,y1)
	if not allow_overflow:
		if (dist_>d):
			return (x2,y2)
	ux = (x2-x1)/d
	uy = (y2-y1)/d

	x = ux*dist_ + x1
	y = uy*dist_ + y1
	return (x,y)
	
#Get current time in seconds
def GetTime():
	"""
	Return the time.

	Returns:
		[float]: Return the time.
	"""
	return app.GetTime()

def GetPlayerEmpireFirstMap():
	empire_id = Data.empireID
	#chat.AppendChat(empire_id)
	empires_map_names = {
		1: 'metin2_map_a1',
		2: 'metin2_map_b1',
		3: 'metin2_map_c1',
	}
	return empires_map_names[empire_id]

def GetPlayerEmpireSecondMap():
	empire_id = Data.empireID
	#chat.AppendChat(empire_id)
	empires_map_names = {
		1: 'metin2_map_a3',
		2: 'metin2_map_b3',
		3: 'metin2_map_c3',
	}
	return empires_map_names[empire_id]	

#Return a tupple, the first value is true or false according if the timer has been reached, and the second value is the current timer
#if first value is true or the old timer if false
def timeSleep(last_time,sleepTime):
	"""
	Helper function to simlate a timer.
	Return a tupple, the first argument is true or false according if the timer has been reached, and the second argument is the current timer
	if first value is true or the old timer if false

	Args:
		last_time ([float]): The last time slept (seconds).
		sleepTime ([float]): The amount of sleep time (seconds).
	
	Returns:
		[(bool,float)]: Returns a bool that is true or false according if the timer has been reached, and a time containing the last time it slept.
	"""
	timer = GetTime()
	if(last_time<timer-sleepTime):
		return(True,timer)
	return(False,last_time)

#Writes to a file located in Extractor folder inside client folderP
def extractFile(path):
	"""
	Extracts a pack encrypted file.
	The unencrypted file is stored in Extractor directory.

	Args:
		path ([str]): The path of the file related to the EtherPacket file structure.
	"""
	import os
	initial_folder = eXLib.PATH+"Extractor\\"
	_str = eXLib.Get(path)
	file_location = initial_folder + path.replace(":","_")
	
	if not os.path.exists(os.path.dirname(file_location)):
		os.makedirs(os.path.dirname(file_location))
		

	with open(file_location, "wb") as myfile:
		myfile.write(_str)

def dist(x1,y1,x2,y2):
	"""
	Return distance between 2 points.

	Args:
		x1 ([int]): x1
		y1 ([int]): y1
		x2 ([int]): x2
		y2 ([int]): y2

	Returns:
		[float]: Returns distance between points.
	"""
	return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
	
def GetNextChannel():
	from OpenBot.Modules import ChannelSwitcher
	current_channel = GetCurrentChannel()
	if not current_channel:
		return 0
	ChannelSwitcher.instance.GetChannels()
	if current_channel + 1 > len(ChannelSwitcher.instance.channels):
		current_channel = 1
	else:
		current_channel += 1
	
	return current_channel

def GetPreviousChannel():
	from OpenBot.Modules import ChannelSwitcher
	current_channel = GetCurrentChannel()
	if not current_channel:
		return 0
	ChannelSwitcher.instance.GetChannels()	
	if current_channel - 1 < 1:
		current_channel = len(ChannelSwitcher.instance.channels)
	else:
		current_channel -= 1
	
	return current_channel
	
def GetCurrentChannel():
	"""
	Returns the current channel based on the string under the minimap.

	Returns:
		[int]: Returns the channel, or 0 in case of an exception raised.
	"""
	try:
		return int(Data.serverInfo.split(',')[1][3:])
	except:
		OpenLog.DebugPrint("Exception raised when trying to obtain current channel.")
		return 0

def GetCurrentServer():
	try:
		return Data.serverInfo.split(',')[0]
	except:
		OpenLog.DebugPrint("Exception raised when trying to obtain current channel.")
		return 0

def IsWeaponArch():
	"""
	Return true if weapon is arch
	"""
	idx = player.GetItemIndex(player.EQUIPMENT, item.EQUIPMENT_WEAPON)
	if idx == 0:
		return False
	item.SelectItem(idx)
	if item.GetItemType() == item.ITEM_TYPE_WEAPON and item.GetItemSubType() == item.WEAPON_BOW:
		return True
	return False

def IsWeaponPickaxe():
	"""
		Return true if weapon is pickaxe
	"""
	idx = player.GetItemIndex(player.EQUIPMENT, item.EQUIPMENT_WEAPON)
	if idx == 0:
		return False
	item.SelectItem(idx)
	if item.GetItemType() == item.ITEM_TYPE_PICK:
		return True
	return False

def SetTimerFunction(time,function):
	"""
	Executes a function after a specified period of time in seconds. 
	"""
	function_handler.RegisterOnEventExit(time,function)


class TimeFunctionHandler(ui.ScriptWindow):

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.function_list = []


	def RegisterOnEventExit(self,time,function):
		self.function_list.append({"time":GetTime()+time,"function":function})

	def OnUpdate(self):
		curTime = GetTime()
		to_del = []
		for i,func in enumerate(self.function_list):
			if curTime >= func["time"]:
				func["function"]()
				to_del.append(i)
		
		for i in to_del:
			del self.function_list[i]


class WaitingDialog(ui.ScriptWindow):

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.eventTimeOver = lambda *arg: None
		self.eventExit = lambda *arg: None

	def __del__(self):
		ui.ScriptWindow.__del__(self)

	def Open(self, waitTime):
		curTime = time.clock()
		self.endTime = curTime + waitTime
		self.Show()		

	def Close(self):
		self.Hide()

	def SAFE_SetTimeOverEvent(self, event):
		self.eventTimeOver = ui.__mem_func__(event)

	def SAFE_SetExitEvent(self, event):
		self.eventExit = ui.__mem_func__(event)
		
	def OnUpdate(self):
		lastTime = max(0, self.endTime - time.clock())
		if 0 == lastTime:
			self.Close()
			self.eventTimeOver()
		else:
			return
		
	def OnPressExitKey(self):
		self.Close()
		return True
		
class Item(ui.ListBoxEx.Item):
	def __init__(self, fileName):
		ui.ListBoxEx.Item.__init__(self)
		self.canLoad=0
		self.text=fileName
		self.textLine=self.__CreateTextLine(fileName)          

	def __del__(self):
		ui.ListBoxEx.Item.__del__(self)

	def GetText(self):
		return self.text

	def SetSize(self, width, height):
		ui.ListBoxEx.Item.SetSize(self, 6*len(self.textLine.GetText()) + 4, height)

	def __CreateTextLine(self, fileName):
		textLine=ui.TextLine()
		textLine.SetParent(self)
		textLine.SetPosition(0, 0)
		textLine.SetText(fileName)
		textLine.Show()
		return textLine	

class EterPackOperator(object):

	def __init__(self, filename):
		#if not pack.Exist(filename):
			#raise IOError, 'No file or directory'
		self.data = self.GetTextFile(filename)
		self.data=_chr(10).join(self.data.split(_chr(13)+_chr(10)))
 
	def read(self, len = None):
		if not self.data:
			return ''
		if len:
			tmp = self.data[:len]
			self.data = self.data[len:]
			return tmp
		else:
			tmp = self.data
			self.data = ''
			return tmp

	def readlines(self):
		Array = str(self.data).split("\n")
		return Array
		
	def getline(self, line):
		return self.readlines()[line - 1]
		
	def getlinecount(self):
		return len(self.readlines())

	def GetTextFile(self, file):
		tmp = []
		try:
			Handle = app.OpenTextFile(file)
			CountLines = app.GetTextFileLineCount(Handle)
		except:
			return ""
		for i in xrange(CountLines):
			line = app.GetTextFileLine(Handle, i)
			if line != "":
				tmp.append(line + "\n")
		app.CloseTextFile()
		return("".join(tmp))

		
#LoadDictFile(CONFIG_PSHOP_AUTO_BUY,SEARCH_ITEMS_MAX_PRICE,float)
FileManager.LoadDictFile(FileManager.CONFIG_BOSSES_ID, BOSS_IDS, int)
FileManager.LoadDictFile(FileManager.CONFIG_ORES_ID, ORES_IDS, int)
Hooks._debugHookFunctionArgs(event.SelectAnswer)
function_handler = TimeFunctionHandler()
function_handler.Show()
import Movement