import eXLib,ui,net,chr,player,chat,item
import OpenLib,NPCInteraction,FileManager,Movement,UIComponents,Settings
from FileManager import boolean

def _PositionRestoreCallback():
	chat.AppendChat(3,"[Fishing-bot] Returning from NPC.")
	instance.startFishing()

def _PlaceFireCallBack():
	chat.AppendChat(3,"[Fishing-bot] Setting CampFire.")
	instance.PlaceFireAndGrillFish()


GOLD_RING = 50002
GOLD_PIECE = 80008
GOLD_KEY = 50008
SILVER_KEY = 50009
MERMAID_KEY = 50043
SHRIMP = 27798
CARPA = 27806
class FishingBotDialog(ui.Window):


	STATE_WAITING= 0
	STATE_FISHING= 1
	STATE_GOING_TO_SHOP = 2
	STATE_IMPROVING_ROD = 3
	STATE_PLACE_FIRE = 4

	def __init__(self):
		ui.Window.__init__(self)
		self.Show()
		self.catches = {key : {} for key in range(27802,27832)}
		self.toFryFish = set(self.catches.keys())
		self.toFryFish |= {fish for fish in range(27833,27862)}
		self.deadFish = {key for key in range(27833,27862)}
		self.liveFish = {key for key in range(27803,27832)}
		self.friedFish = {key for key in range(27863,27892)}

		#Extra stuff like rings
		self.catches[GOLD_RING] = {}  #Gold Ring
		self.catches[70049] = {}
		self.catches[70051] = {}
		self.catches[70050] = {}
		self.catches[70048] = {}
		self.catches[GOLD_KEY] = {}
		self.catches[MERMAID_KEY] = {}
		self.catches[GOLD_PIECE] = {}
		self.catches[SILVER_KEY] = {}
		self.catches[SHRIMP] = {}

		self.campFire = 27600
		self.campFireRace = 12000


		self.fishIds = [key for key in range(27802,27832)]
		self.state = self.STATE_WAITING
		self.minnowID = 27802
		self.wormID = 27801
		self.pasteID = 27800
		self.images = []
		self.hairIDs = [key for key in range(70201,70207)] 
		self.isRodDown = False
		self.startPosition = (0,0)
		self.isMoving = False
		self.BuildWindow()

	def __del__(self):
		ui.Window.__del__(self)

	def BuildWindow(self):
		self.Board = ui.BoardWithTitleBar()
		self.Board.SetSize(390, 500)
		self.Board.SetCenterPosition()
		self.Board.AddFlag('movable')
		self.Board.AddFlag('float')
		self.Board.SetTitleName('FishBot')
		self.Board.SetCloseEvent(self.Close)
		self.Board.Hide()
		self.comp = UIComponents.Component()

		self.enableButton = self.comp.OnOffButton(self.Board, '', '', 165, 435, OffUpVisual='OpenBot/Images/start_0.tga', OffOverVisual='OpenBot/Images/start_1.tga', OffDownVisual='OpenBot/Images/start_2.tga',OnUpVisual='OpenBot/Images/stop_0.tga', OnOverVisual='OpenBot/Images/stop_1.tga', OnDownVisual='OpenBot/Images/stop_2.tga',funcState= self.StartStopEvent, defaultValue=False)
		
  		#self.useFishBait = self.comp.OnOffButton(self.Board, '   Use fish as bait', '', 140, 380)
		
  		self.waitNum = self.comp.TextLine(self.Board, '100', 330, 347, self.comp.RGB(255, 255, 255))
		self.serverNum = self.comp.TextLine(self.Board, '100', 330, 367, self.comp.RGB(255, 255, 255))
		self.startStopNum = self.comp.TextLine(self.Board, '100', 330, 387, self.comp.RGB(255, 255, 255))

		self.l2 = self.comp.TextLine(self.Board, 'Wait after fish', 35, 347, self.comp.RGB(255, 255, 255))
		self.l1 = self.comp.TextLine(self.Board, 'Time left fishing(server)', 35, 367, self.comp.RGB(255, 255, 255))
		self.val = self.comp.TextLine(self.Board, 'Time fishing', 35, 387, self.comp.RGB(255, 255, 255))
		
		self.WaitDelaySlider = self.comp.SliderBar(self.Board, 0.0, self.WaitDelay_func, 140, 350)
		self.ServerDelaySlider = self.comp.SliderBar(self.Board, 0.0, self.ServerDelay_func, 140, 370)
		self.StartStopDelaySlider = self.comp.SliderBar(self.Board, 0.0, self.StartStopDelay_func, 140, 390)

		#Grill button and image
		item.SelectItem(self.campFire)
		itemIcon = item.GetIconImageFileName()
		self.campfireimg = self.comp.ExpandedImage(self.Board, 248, 420, str(itemIcon))
		self.grillFishBtn = self.comp.Button(self.Board, 'Grill Fish', '', 235, 455, self.PlaceFireAndGrillFish, 'd:/ymir work/ui/public/middle_button_01.sub', 'd:/ymir work/ui/public/middle_button_02.sub','d:/ymir work/ui/public/middle_button_03.sub')
		
		##HairButton
		item.SelectItem(70201)
		itemIcon = item.GetIconImageFileName()
		self.hairBtn = self.comp.OnOffButton(self.Board, '', 'Drop', 320, 432, image=itemIcon)

		#Worm Btn
		item.SelectItem(self.wormID)
		itemIcon = item.GetIconImageFileName()
		self.buyWormsBtn = self.comp.OnOffButton(self.Board, '', 'Got to shop and buy Worms',  65, 430,image=str(itemIcon))

		#Rod Btn
		item.SelectItem(27590) #Fishing Rod +20
		itemIcon = item.GetIconImageFileName()
		self.rodBtn = self.comp.OnOffButton(self.Board, '', 'Level up Rod automatically',  10, 390,image=str(itemIcon),yImgOffset=70,xImgOffset=25)
		self.rodBtn.SetOff()

		step_x = 44
		step_y = 60
		
		min_x = 25
		min_y = 40
		max_x = 370

		current_x = min_x
		current_y = min_y
		
		
		for id in self.catches.keys():
			if current_x > max_x:
				current_x = min_x
				current_y += step_y
			item.SelectItem(id)
			itemIcon = item.GetIconImageFileName()
			self.images.append(self.comp.ExpandedImage(self.Board, current_x, current_y, str(itemIcon)))

			if id == self.minnowID or id == SHRIMP:
				self.catches[id]['buttonBait'] = self.comp.OnOffButton(self.Board, '', 'Use as bait', current_x, current_y + 30)
			elif id in self.fishIds:
				self.catches[id]['buttonOpen'] = self.comp.OnOffButton(self.Board, '', 'Kill Fish', current_x, current_y + 30)
			if id == GOLD_RING or id == 70049 or id == 70051 or id == 70050 or id == 70048 or id == GOLD_PIECE or id == GOLD_KEY or id == SILVER_KEY or id == MERMAID_KEY:
				self.catches[id]['buttonSell'] = self.comp.OnOffButton(self.Board, '', 'Sell', current_x, current_y + 30)
			if id != GOLD_RING and id != GOLD_PIECE:
				self.catches[id]['buttonDrop'] = self.comp.OnOffButton(self.Board, '', 'Drop', current_x + 15, current_y + 30)

			current_x += step_x
		self.buyWormsBtn.SetOff()

		self.loadSettings()
		
		self.lastTime = 0
		self.lastTimeFishState = 0
		self.lastTimeWaitState = 0
		self.lastTimeImprove = 0
		self.lastTimeFire = 0

		self.WaitDelay_func()
		self.ServerDelay_func()
		self.StartStopDelay_func()

	def loadSettings(self):
		for fish_id in self.catches.keys():
			for fishButtonName in self.catches[fish_id].keys():
				self.catches[fish_id][fishButtonName].SetValue(boolean(FileManager.ReadConfig("FishBot_" + str(fish_id) + "_" + fishButtonName)))
		self.WaitDelaySlider.SetSliderPos(float(FileManager.ReadConfig("FishBot_WaitDelay")))
		self.ServerDelaySlider.SetSliderPos(float(FileManager.ReadConfig("FishBot_ServerDelay")))
		self.StartStopDelaySlider.SetSliderPos(float(FileManager.ReadConfig("FishBot_StartStopDelay")))
		self.hairBtn.SetValue(boolean(FileManager.ReadConfig("FishBot_HairDyes")))
		self.buyWormsBtn.SetValue(boolean(FileManager.ReadConfig("FishBot_BuyWorms")))
		self.rodBtn.SetValue(boolean(FileManager.ReadConfig("FishBot_rodUpgrade")))


	def StartStopEvent(self,val):
		if not val:
			NPCInteraction.StopAction()
			self.exitFishing()
		else:
			self.startPosition = player.GetMainCharacterPosition()
			#eXLib.BlockFishingPackets()
			chat.AppendChat(3,"[Fishing-bot] ATTENTION, you should only have one rod in you inventory!")
			self.startFishing()

	def saveSettings(self):
		for fish_id in self.catches.keys():
			for fishButtonName in self.catches[fish_id].keys():
				name = "FishBot_" + str(fish_id) + "_" + fishButtonName
				value = self.catches[fish_id][fishButtonName].isOn
				FileManager.WriteConfig(name,str(value))
		FileManager.WriteConfig("FishBot_WaitDelay", str(self.WaitDelaySlider.GetSliderPos()))
		FileManager.WriteConfig("FishBot_ServerDelay", str(self.ServerDelaySlider.GetSliderPos()))
		FileManager.WriteConfig("FishBot_StartStopDelay", str(self.StartStopDelaySlider.GetSliderPos()))
		FileManager.WriteConfig("FishBot_HairDyes", str(self.hairBtn.isOn))
		FileManager.WriteConfig("FishBot_BuyWorms", str(self.buyWormsBtn.isOn))
		FileManager.WriteConfig("FishBot_rodUpgrade", str(self.rodBtn.isOn))
		FileManager.Save()

	def isRodAbleToLevelUp(self):
		idx = player.GetItemIndex(player.EQUIPMENT,item.EQUIPMENT_WEAPON)
		if(idx == 0):
			return False	
		item.SelectItem(idx)

		currPoints = player.GetItemMetinSocket(player.EQUIPMENT,item.EQUIPMENT_WEAPON,0)
		maxPoints = item.GetValue(2)

		if currPoints == maxPoints and item.GetItemType() == item.ITEM_TYPE_ROD:
			chat.AppendChat(3,"[Fishing-Bot] Rod is ready to be upgraded.")
			return True
		return False

	def SetState(self,stateChange):
		self.state = stateChange


	def LevelUpRod(self):
		self.SetState(self.STATE_IMPROVING_ROD)
		self.stopFishing()
		if self.isMoving:
			return
		
		#Unequip weapon if it is a rod
		val = OpenLib.isItemTypeOnSlot(item.ITEM_TYPE_ROD,player.EQUIPMENT,item.EQUIPMENT_WEAPON)
		if val:
			chat.AppendChat(3,"[Fishing-Bot] Removing fishing rod from main weapon")
			net.SendItemUsePacket(player.EQUIPMENT,item.EQUIPMENT_WEAPON)
			return
		
		
		slot = OpenLib.GetItemByType(item.ITEM_TYPE_ROD)

		#Check if rod is already in inventory
		if slot == -1:
			chat.AppendChat(3,"[Fishing-Bot] Rod is not in inventory")
			return

		chat.AppendChat(3,"[Fishing-Bot] Request to shop sent")
		NPCInteraction.RequestGiveItemNPCAwayRestorePosition([slot],NPCInteraction.GetFishermanUpgrade(),callback=_PositionRestoreCallback,pos=self.startPosition)
		self.isMoving = True
	
	def GrillFishes(self,vid):
		for i in range(0,OpenLib.MAX_INVENTORY_SIZE):
			id = player.GetItemIndex(i)
			if id == 0:
				continue
			if id in self.toFryFish and id != CARPA:
				net.SendGiveItemPacket(vid,player.SLOT_TYPE_INVENTORY,i,player.GetItemCount(i))

	def GoToShop(self):
		self.stopFishing()
		#if self.isRodDown:
		#	self.isRodDown = False
		#	eXLib.SendStopFishing(eXLib.UNSUCCESS_FISHING,0)
		#Check items to sell
		to_sell = set()
		has_worms = False
		has_fire = False
		for i in range(0,OpenLib.MAX_INVENTORY_SIZE):
			idx = player.GetItemIndex(i)
			if idx != 0:
				if idx in self.catches:
					fishOptions = self.catches[idx]
					if 'buttonSell' in fishOptions.keys() and fishOptions['buttonSell'].isOn:
						to_sell.add(i)
				else:
					#Check if have worms and campfire
					if self.wormID == idx:
						has_worms = True
					if self.campFire == idx:
						has_fire = True
		to_sell=to_sell.union(Settings.GetSlotItemsToSell())
		to_buy = []
		if not has_worms:
			for i in range(0,5):
				to_buy.append(7)
		
		if not has_fire:
			to_buy.append(1)

		self.isMoving = True



		#GoShop and use campfire
		NPCInteraction.RequestBusinessNPCAway(to_buy,to_sell,NPCInteraction.GetFishermanShop(),callback=_PlaceFireCallBack)
		chat.AppendChat(3,"[Fishing-Bot] Selling slots: "+str(to_sell))
		#NPCInteraction.RequestBusinessNPCAwayRestorePosition(to_buy,to_sell,NPCInteraction.FISHERMAN_SHOP,callback=_PositionRestoreCallback,pos=self.startPosition)
		self.SetState(self.STATE_GOING_TO_SHOP)

	def exitFishing(self):		
		self.stopFishing()

	def startFishing(self):
		self.SetState(self.STATE_WAITING)
		eXLib.BlockFishingPackets()

	def stopFishing(self):
		if self.isRodDown:
			eXLib.SendStopFishing(eXLib.UNSUCCESS_FISHING,0)
			self.isRodDown = False
		eXLib.UnblockFishingPackets()
	
	def WaitDelay_func(self):
		self.waitDelay = int(self.WaitDelaySlider.GetSliderPos()*10)
		self.waitNum.SetText(str(self.waitDelay)+ ' s')
  
	def ServerDelay_func(self):
		self.serverDelay = int(self.ServerDelaySlider.GetSliderPos()*10)
		self.serverNum.SetText(str(self.serverDelay) + ' s')
	
	def StartStopDelay_func(self):
		self.startStopDelay= float(self.StartStopDelaySlider.GetSliderPos())
		self.startStopNum.SetText(str(int(self.startStopDelay*10)) + ' s')

	def PlaceFireAndGrillFish(self):
		slot = OpenLib.GetItemByID(self.campFire)
		if slot != -1:
			net.SendItemUsePacket(slot)
			self.SetState(self.STATE_PLACE_FIRE)
			return
		chat.AppendChat(3,"[Fishing-bot] You need to buy a campfire first.")

	
	
	def switch_state(self):
		if self.Board.IsShow():
			self.Board.Hide()
			self.saveSettings()
		else:
			self.Board.Show()
			self.loadSettings()

	def CheckInv(self):
		fishIds = self.catches.keys()
		useBait = False
		dropFish = False
		wormSlot = -1
		pastSlot = -1

		#Check bait and fish killing
		for i in range(0,OpenLib.MAX_INVENTORY_SIZE):
			id = player.GetItemIndex(i)
			if self.wormID == id:
				wormSlot = i
			if self.pasteID == id:
				pastSlot = i
			if dropFish == False and id in self.hairIDs and self.hairBtn.isOn:
				dropFish = True
				net.SendItemDropPacketNew(i,200)
				continue

			if id in self.liveFish:
				isAliveFish = True
			else:
				isAliveFish = False
			if id in self.deadFish:
				id -=30
				isDeadFish = True
			else:
				isDeadFish = False

			if id in self.friedFish:
				id-=60
				isFryFish = True
			else:
				isFryFish = False



			if id in fishIds:
				fishOptions = self.catches[id]

				if useBait == False and 'buttonBait' in fishOptions.keys() and fishOptions['buttonBait'].isOn and not isDeadFish and not isFryFish:
					net.SendItemUsePacket(i)
					useBait = True
					continue
				if 'buttonOpen' in fishOptions.keys() and fishOptions['buttonOpen'].isOn and not isDeadFish and not isFryFish:
					net.SendItemUsePacket(i)
					continue
				if dropFish == False and 'buttonDrop' in fishOptions.keys() and fishOptions['buttonDrop'].isOn:
					dropFish = True
					net.SendItemDropPacketNew(i,player.GetItemCount(i))
					continue
		
		#Check if inventory is full
		if OpenLib.isInventoryFull():
			self.GoToShop()
			return False

		#Check if rod is available
		val = OpenLib.isItemTypeOnSlot(item.ITEM_TYPE_ROD,player.EQUIPMENT,item.EQUIPMENT_WEAPON)
		if val == 0:
			slot = OpenLib.GetItemByType(item.ITEM_TYPE_ROD)
			if slot == -1:
				chat.AppendChat(3,"[Fishing-Bot] No rod available, you need a rod first")
				self.exitFishing()
				return False
			else:
				net.SendItemUsePacket(slot)
				return False
		#Check if rod is ready to level up
		if self.rodBtn.isOn and self.isRodAbleToLevelUp():
			self.state = self.STATE_IMPROVING_ROD
			return False

		#Check for next bait to use
		if useBait == False:
			if wormSlot != -1:
				net.SendItemUsePacket(wormSlot)
				return True
			elif pastSlot != -1:
				net.SendItemUsePacket(pastSlot)
				return True
			else:
				if self.buyWormsBtn.isOn:
					self.GoToShop()
					return False
				else:
					self.exitFishing()
					chat.AppendChat(3,"[Fishing-Bot] No Worms left.")
					return False

		return True
   
				
	def OnUpdate(self):
		val, self.lastTime = OpenLib.timeSleep(self.lastTime,0.1)
		if(val and self.enableButton.isOn and OpenLib.IsInGamePhase()):
			if self.state == self.STATE_WAITING:
				valWaitState, self.lastTimeWaitState = OpenLib.timeSleep(self.lastTimeWaitState,self.WaitDelaySlider.GetSliderPos()*10)
				if valWaitState:
					if self.CheckInv() == False:
						return
					eXLib.SendStartFishing(2)
					chat.AppendChat(3,"[Fishing-Bot] Using bait, and start fishing")
					self.SetState(self.STATE_FISHING)
					self.lastTimeFishState = OpenLib.GetTime()
					self.isRodDown = True
					self.isMoving = False
					
			if self.state == self.STATE_FISHING:
				valFishState, self.lastTimeFishState = OpenLib.timeSleep(self.lastTimeFishState,self.StartStopDelaySlider.GetSliderPos()*10)
				if valFishState:
					chat.AppendChat(3,"[Fishing-Bot] Pulling Rod")
					eXLib.SendStopFishing(eXLib.SUCCESS_FISHING,self.ServerDelaySlider.GetSliderPos()*10)
					self.lastTimeWaitState = OpenLib.GetTime()
					self.SetState(self.STATE_WAITING)
					self.isRodDown = False

			if self.state == self.STATE_GOING_TO_SHOP:
				#The callback will take care of leaving the state
				pass
			
			if self.state == self.STATE_IMPROVING_ROD:
				val, self.lastTimeImprove = OpenLib.timeSleep(self.lastTimeImprove,0.5)
				if not val:
					return

				self.LevelUpRod()

		if self.state == self.STATE_PLACE_FIRE:
			val, self.lastTimeFire = OpenLib.timeSleep(self.lastTimeFire,0.2)
			if not val:
				return
			for vid in eXLib.InstancesList:
				chr.SelectInstance(vid)
				race = chr.GetRace()
				if race == self.campFireRace:
					self.GrillFishes(vid)
					if self.enableButton.isOn:
						Movement.GoToPositionAvoidingObjects(self.startPosition[0],self.startPosition[1],callback=_PositionRestoreCallback,maxDist=250)
						self.SetState(self.STATE_GOING_TO_SHOP)
					else:
						self.SetState(self.STATE_WAITING)
		

	
	def Close(self):
		self.Board.Hide()
		self.saveSettings()


def switch_state():
	instance.switch_state()

instance = FishingBotDialog()