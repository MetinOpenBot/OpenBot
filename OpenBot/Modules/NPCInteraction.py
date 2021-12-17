import eXLib,ui,net,chr,player,chat,shop,event,background
import OpenLib, Movement, Hooks, MapManager, OpenLog, Data



STATE_NONE = 0
STATE_WAITING_OPEN_SHOP = 1
STATE_BUYING = 2
STATE_SELLING = 3
STATE_FINISH_SHOPPING = 4
STATE_GIVING_ITEMS = 5

#Tim after each loop
TIME_WAIT = 0.2

#Time Buy
TIME_BUY = 0.55

TIME_SELL = 0.55
TIME_GIVE_ITEM = .5


"""
Module responsible for buying selling and any other interaction with NPC's.
BETA
"""


#NPC OPTIONS
#Creates an NPC action
#If map of the npc is unknown
#If the position is not specified it will find the closest NPC on that map
class NPCAction:
	"""
	This class represents an NPCAction to be processed later by this module.
	The actions can be moving to an NPC, clicking on it and selecting the event answers.
	To create an action, it just needs the Race of the NPC and the event_answers in case it is needed, the module will later find the NPC in the maps. 
	"""
	def __init__(self,race,position=None,event_answer=[],_map=None):
		"""
		Constructor to create action

		Args:
			race ([int]): The race of the NPC.
			position ([(float,float)], optional): The position (x,y) of the NPC if not set, it will try to find the closest NPC if it is in a different map. Defaults to None.
			event_answer (list, optional): A list of indexes containing the index of the event answers. Defaults to [].
			_map ([str], optional): A map name, if not set, it will use the current map. Defaults to None.
		"""
		self.race = race
		self.event_answer = event_answer
		self.position = position
		self.mapName = _map

		if self.mapName == None:
			map_path,self.mapName = MapManager.GetClosestMapPathWithNPC(self.race)

		if self.position == None:
			self.position=MapManager.GetNpcFromMap(self.mapName, self.race)

		OpenLog.DebugPrint("[NPC-ACTION] - New NPC Action race "+str(self.race)+" on map " + str(self.mapName) + " at position "+ str(self.position))

	def GetNpcPosition(self):
		return self.position

	def DoAction(self):
		vid = self.SearchVIDClosest()
		#OpenLog.DebugPrint(str(vid))
		if vid:
			OpenLog.DebugPrint("[NPC-ACTION] - Doing NPC Action")
			net.SendOnClickPacket(vid)
			OpenLib.skipAnswers(self.event_answer, False)
			return True
		return False

	def GoToPosition(self,callback=None):
		return Movement.GoToPositionAvoidingObjects(self.position[0],self.position[1],mapName=self.mapName,callback=callback)


#Gets the closest vid from the race
#if the race doesn't exist closeby returns None
	def SearchVIDClosest(self):
		npcs = dict()
		for vid in eXLib.InstancesList:
			chr.SelectInstance(vid)
			curr_race = chr.GetRace()
			if self.race == curr_race:
				dist = player.GetCharacterDistance(vid)
				npcs[vid] = dist
		if len(npcs) == 0:
			return None
		min_vid = min(npcs.keys(), key=(lambda k: npcs[k]))
		return min_vid

#This should be passed in the interface function to select the NPC
#First value is race, second value is the SelectAnswer arguments as a tupple, provide None if not needed


def GetFishermanShop():
	"""
	Get an NPC action that opens FishermanShop.

	Returns:
		[NPCAction]: An NPC Action.
	"""
	return NPCAction(9009,event_answer=[1])

def GetFishermanUpgrade():
	"""
	Get an NPC action that upgrades the fishingrod at the fisherman.

	Returns:
		[NPCAction]: An NPC Action.
	"""
	return NPCAction(9009,event_answer=[0,0])

#def GetFishermanCarpa():
#	return NPCAction(9009,event_answer=[5,0])

def GetGeneralShop():
	"""
	Get an NPC action that opens the general store.

	Returns:
		[NPCAction]: An NPC Action.
	"""
	return NPCAction(9003,event_answer=[0,0])


#Call SetOrder to set npc and order and call StartNPCBusiness aftwerwards to start business
class NPCInteractionDialog(ui.ScriptWindow):
	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.Show()
		Data.time_NPCInteraction_lastTime = 0
		self.buyItems_list =list()
		self.sellItems_list =list()
		self.giveItems_list =list()
		self.ableToBuy = True
		self.State = STATE_NONE
		self.vid = 0
		Data.time_NPCInteraction_lastTimeBuy = 0
		self.callback = None
		self.npcAction = 0
		Data.time_NPCInteraction_lastTimeSell = 0
		Data.time_NPCInteraction_lastTimeGive = 0
		


	def OpenShop(self):
		return self.npcAction.DoAction()

	def StartNPCBusiness(self,open_shop=True):
		Hooks.questHook.HookFunction()
		if open_shop:
			if not self.OpenShop():
				self.State = STATE_FINISH_SHOPPING
				chat.AppendChat(3,"[NPCInteraction] NPC with Race:"+str(self.npcAction.race)+" is not close by")
				return False
		self.State = STATE_WAITING_OPEN_SHOP
		return True

	#Needs to be called before StartNPCBusiness
	def SetOrder(self,npc_action,buy_list,sell_list,callback=None):
		self.buyItems_list = list(buy_list)
		self.sellItems_list = list(sell_list)
		self.npcAction = npc_action
		self.callback = callback


	def EndNPCBusiness(self):
		if(self.callback != None):
			self.callback()
			self.callback = None
			#chat.AppendChat(3,"Calling callback")
		self.State = STATE_NONE
		net.SendShopEndPacket()
		Hooks.questHook.UnhookFunction()

	#Give Item Stuff
	def SetGiveItemsToNPC(self,npc_action,give_items_list,callback=None):
		self.giveItems_list = give_items_list
		self.npcAction = npc_action
		self.callback = callback

	def StartNPCGiveItem(self):
		Hooks.questHook.HookFunction()
		self.State = STATE_GIVING_ITEMS
		return True

	def EndNPCGiveItem(self):
		if(self.callback != None):
			self.callback()
			self.callback = None
		self.State = STATE_NONE
		Hooks.questHook.UnhookFunction()
		return True


	def OnUpdate(self):
		val, Data.time_NPCInteraction_lastTime = OpenLib.timeSleep(Data.time_NPCInteraction_lastTime,TIME_WAIT)
		if not val or self.State == STATE_NONE or not OpenLib.IsInGamePhase():
			return
		if self.State == STATE_WAITING_OPEN_SHOP:
			#chat.AppendChat(3,"Waiting for shop to be open.")
			if shop.IsOpen():
				self.State = STATE_SELLING
				return
			self.OpenShop()
			

		if self.State == STATE_SELLING:
			val, Data.time_NPCInteraction_lastTimeSell = OpenLib.timeSleep(Data.time_NPCInteraction_lastTimeSell,TIME_SELL)
			if val:
				if len(self.sellItems_list) == 0:
					self.State = STATE_BUYING
					return
				slot = self.sellItems_list.pop(0)
				net.SendShopSellPacketNew(slot,player.GetItemCount(slot),1)
				chat.AppendChat(3,"[NPC-SHOPER] Sold item at slot " + str(slot))
			return

		if self.State == STATE_BUYING:
			val, Data.time_NPCInteraction_lastTimeBuy = OpenLib.timeSleep(Data.time_NPCInteraction_lastTimeBuy,TIME_BUY)
			if(val):
				if len(self.buyItems_list) == 0:
					self.State = STATE_FINISH_SHOPPING
					return
				slot = self.buyItems_list.pop(0)
				net.SendShopBuyPacket(slot)
			else:
				return

		if self.State == STATE_FINISH_SHOPPING:
			self.EndNPCBusiness()
			return

		if self.State == STATE_GIVING_ITEMS:
			val, Data.time_NPCInteraction_lastTimeGive = OpenLib.timeSleep(Data.time_NPCInteraction_lastTimeGive,TIME_GIVE_ITEM)
			if not val:
				return
			if len(self.giveItems_list) == 0:
				self.EndNPCGiveItem()
				return
			else:
				vid = self.npcAction.SearchVIDClosest()
				if vid== None:
					#chat.AppendChat(3,"[NPC-GIVER] No NPC with vid " +str(vid)+" is close.")
					self.EndNPCGiveItem()
					return
				else:
					slot = self.giveItems_list.pop()
					#chat.AppendChat(3,"[NPC-GIVER] Giving "+  str(player.GetItemCount(slot)) + " item(s) at slot " +str(slot)+" to VID " +str(vid))
					net.SendGiveItemPacket(vid,player.SLOT_TYPE_INVENTORY,slot,player.GetItemCount(slot))
					OpenLib.skipAnswers(self.npcAction.event_answer)
	
	def __del__(self):
		ui.ScriptWindow.__del__(self)


#Used to move back to original position
originalPosition = (0,0,0)
originalFunctionCallback = None

#Called by Movement module
def _StartBusinessProcessCallBack():
	OpenLog.DebugPrint("[NPCInteraction] Starting Business Process")
	instance.StartNPCBusiness(True)

#Called by Movement module
def _StartGiveItemProcessCallBack():
	OpenLog.DebugPrint("[NPCInteraction] Starting item give operation")
	instance.StartNPCGiveItem()

#Called by this module
def _ReturnToPositionCallBack():
	#global originalFunctionCallback
	OpenLog.DebugPrint("[NPCInteraction] Going to original position: "+str(originalPosition))
	Movement.GoToPositionAvoidingObjects(originalPosition[0],originalPosition[1],callback=originalFunctionCallback)
	#originalFunctionCallback = None


###############################
##########INTERFACE############
###############################
#DO NOT CALL THIS MULTIPLE TIMES WITHOUT FINISHING THE PROCESS

#############SHOPER#############
#The answer bypass will be applied before the shop is opened

def RequestBusinessNPCClose(buy_items_list,sell_items_list,npc,callback=None,open_shop=True):
	"""
	Buy and Sell the items specified to an NPC close by. 

	Args:
		buy_items_list ([list]): list containing the items(slots) to be bought.
		sell_items_list ([list]): list containing the items(slots) to be sold.
		npc ([NPCAction]): An NPC Action, see above.
		callback ([function], optional): A function callback to called after finish the business. Defaults to None.
		open_shop (bool, optional): If true will first open the shop. Defaults to True.
	"""
	instance.SetOrder(npc,buy_items_list,sell_items_list,callback)
	instance.StartNPCBusiness(open_shop)

def RequestBusinessNPCAway(buy_items_list,sell_items_list,npc,callback=None):
	"""
	Buy and Sell the items specified to an NPC far away. 

	Args:
		buy_items_list ([list]): list containing the items(slots) to be bought.
		sell_items_list ([list]): list containing the items(slots) to be sold.
		npc ([NPCAction]): An NPC Action, see above.
		callback ([function], optional): A function callback to called after finish the business. Defaults to None.
	"""
	instance.SetOrder(npc,buy_items_list,sell_items_list,callback)
	npc.GoToPosition(callback=_StartBusinessProcessCallBack)
	#Movement.GoToPositionAvoidingObjects(npc.position[0],npc.position[1],callback=_StartBusinessProcessCallBack)

#The same as the one before, but it moves to the npc position and comesback
def RequestBusinessNPCAwayRestorePosition(buy_items_list,sell_items_list,npc,callback=None,pos=None):
	"""
	Buy and Sell the items specified to an NPC far away and go back to the specified position. 

	Args:
		buy_items_list ([list]): list containing the items(slots) to be bought.
		sell_items_list ([list]): list containing the items(slots) to be sold.
		npc ([NPCAction]): An NPC Action, see above.
		callback ([function], optional): A function callback to called after finish the business. Defaults to None.
		pos ([(int,int)]): A position to return to. Defaults to player.GetMainCharacterPosition().
	"""
	if pos == None:
		pos=player.GetMainCharacterPosition()
	global originalPosition,originalFunctionCallback
	originalPosition = pos
	originalFunctionCallback = callback
	OpenLog.DebugPrint("[NPCInteraction] Starting restore business operation from " +  str(pos))
	instance.SetOrder(npc,buy_items_list,sell_items_list,_ReturnToPositionCallBack)
	npc.GoToPosition(callback=_StartBusinessProcessCallBack)


def RequestGiveItemNPCClose(give_items_list,npc,callback=None):
	"""
	Give items specified to an NPC close by. 

	Args:
		give_items_list ([type]): list containing the items(slots) to be given.
		npc ([NPCAction]): An NPC Action, see above.
		callback ([function], optional): A function callback to called after finish the business. Defaults to None.
	"""
	instance.SetGiveItemsToNPC(npc,give_items_list,callback)
	instance.StartNPCGiveItem()

#The same as the one before, but it moves to the npc position
def RequestGiveItemNPCAway(give_items_list,npc,callback=None):
	"""
	Give items specified to an NPC far away. 

	Args:
		give_items_list ([type]): list containing the items(slots) to be given.
		npc ([NPCAction]): An NPC Action, see above.
		callback ([function], optional): A function callback to called after finish the business. Defaults to None.
	"""
	instance.SetGiveItemsToNPC(npc,give_items_list,callback)
	npc.GoToPosition(callback=_StartBusinessProcessCallBack)

#The same as the one before, but it moves to the npc position and comesback
def RequestGiveItemNPCAwayRestorePosition(give_items_list,npc,callback=None,pos=None):
	"""
	Give items specified  to an NPC far away and go back to the specified position. 

	Args:
		give_items_list ([type]): list containing the items(slots) to be given.
		npc ([NPCAction]): An NPC Action, see above.
		callback ([function], optional): A function callback to called after finish the business. Defaults to None.
		pos ([(int,int)]): A position to return to. Defaults to player.GetMainCharacterPosition().
	"""
	if pos == None:
		pos=player.GetMainCharacterPosition()
	global originalPosition,originalFunctionCallback
	originalPosition = pos
	originalFunctionCallback = callback
	OpenLog.DebugPrint("[NPCInteraction] Starting restore give item operation from " +  str(pos))
	instance.SetGiveItemsToNPC(npc,give_items_list,_ReturnToPositionCallBack)
	npc.GoToPosition(callback=_StartGiveItemProcessCallBack)

def StopAction():
	"""
	Force Stop Interaction.
	"""
	instance.State = STATE_NONE
	Movement.StopMovement()
	Hooks.questHook.UnhookFunction()


instance = NPCInteractionDialog()
		  
		
		

		