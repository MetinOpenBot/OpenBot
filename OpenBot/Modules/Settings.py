import ui,app,chat,chr,net,player,item,skill,time,game,shop,chrmgr,OpenLib,eXLib
import background,constInfo,miniMap,wndMgr,math,uiCommon,grp,FileManager,UIComponents,Movement,OpenLog
import DmgHacks as Dmg
from FileManager import boolean
import UIComponents

class SettingsDialog(ui.ScriptWindow):
	TIME_DEAD = 5
	TIME_POTS = 0.2
	RED_POTIONS_IDS = [27001,27002,27003,27007,27051,27201,27202,27203]
	BLUE_POTIONS_IDS = [27004,27005,27006,27008,27052,27204,27205,27206,63018]

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.restartHere = False
		self.bluePotions = True
		self.redPotions = True
		self.minMana = 95
		self.minHealth = 80

		self.pickUp = False
		self.pickUpRange = 290
		self.pickUpSpeed = 0.5
		self.pickFilter = set()
		self.excludeInFilter = True
		self.useRangePickup = False

		self.wallHack = False

		self.sellItems = set()


		self.timerPots = 0
		self.timerDead = 0
		self.pickUpTimer = 0
		self.LoadSettings()
		self.BuildWindow()
	
	def BuildWindow(self):
		self.Board = ui.BoardWithTitleBar() 
		self.Board.SetPosition(52, 40)
		self.Board.SetSize(300, 370) 
		self.Board.SetTitleName("Settings")
	#	self.Board.AddFlag("float") 
		self.Board.AddFlag("movable")
		self.Board.SetCloseEvent(self.Close)
		self.Board.Hide()
		
		self.comp = UIComponents.Component()

		self.TabWidget = UIComponents.TabWindow(10,30,300-20,370-40,self.Board,['General','Pickup','Attack','Shop'])
		self.generalTab = self.TabWidget.GetTab(0)
		self.pickupTab = self.TabWidget.GetTab(1)
		self.attackTab = self.TabWidget.GetTab(2)
		self.shopTab = self.TabWidget.GetTab(3)


		#self.MovespeedLabel = self.comp.TextLine(self.generalTab, '300', 256, 68, self.comp.RGB(255, 255, 255))
		#self.AttackspeedLabel = self.comp.TextLine(self.attackTab, '200', 256, 108, self.comp.RGB(255, 255, 255))
		#self.SlideMovespeed = self.comp.SliderBar(self.generalTab, 0.6, self.SlideMove, 66, 70)
		#self.SlideAttackspeed = self.comp.SliderBar(self.attackTab, 0.4, self.SlideAttack, 66, 110)
		
		#self.AttackSpeedButton = self.comp.Button(self.attackTab, '', 'Attack-Speed', 25, 60, self.SetAttackSpeed, 'OpenBot/Images/Shortcuts/attack_0.tga', 'OpenBot/Images/Shortcuts/attack_1.tga', 'OpenBot/Images/Shortcuts/attack_0.tga')
		#self.MoveSpeedButton = self.comp.Button(self.generalTab, '', 'Move-Speed', 25, 110, self.SetMoveSpeed, 'OpenBot/Images/Shortcuts/move_0.tga', 'OpenBot/Images/Shortcuts/move_1.tga', 'OpenBot/Images/Shortcuts/move_0.tga')
		#self.DayButton = self.comp.Button(self.Board, '', 'Day', 25, 120, self.SetDay, 'OpenBot/Images/General/sun_0.tga', 'OpenBot/Images/General/sun_1.tga', 'OpenBot/Images/General/sun_0.tga')
		#self.NightButton = self.comp.Button(self.Board, '', 'Night', 80, 120, self.SetNight, 'OpenBot/Images/General/moon_0.tga', 'OpenBot/Images/General/moon_1.tga', 'OpenBot/Images/General/moon_0.tga')
		
		self.DmgMenuButton = self.comp.Button(self.attackTab, '', 'Damage Hacks', 120, 150, self.OpenDmgMenu,  'OpenBot/Images/General/dmg_0.tga', 'OpenBot/Images/General/dmg_1.tga', 'OpenBot/Images/General/dmg_0.tga')
  		self.OneHandedButton = self.comp.Button(self.attackTab, '', 'One-Handed', 40, 150, self.SetOneHand, 'OpenBot/Images/General/onehand_0.tga', 'OpenBot/Images/General/onehand_1.tga', 'OpenBot/Images/General/onehand_0.tga')
		self.TwoHandedButton = self.comp.Button(self.attackTab, '', 'Two-Handed', 200, 150, self.SetTwoHand, 'OpenBot/Images/General/twohand_0.tga', 'OpenBot/Images/General/twohand_1.tga', 'OpenBot/Images/General/twohand_0.tga')

		##GENERAL
		self.loginBtn = self.comp.OnOffButton(self.generalTab, '\t\t\t\t\t\tAuto Login', '', 20, 150,funcState=self.AutoLoginOnOff,defaultValue=int(self.autoLogin))
		self.reviveBtn = self.comp.OnOffButton(self.generalTab, '\t\t\t\t\t\tAuto Restart Here', '', 20, 130,funcState=self.ReviveOnOff,defaultValue=int(self.restartHere))
		self.WallHackBtn = self.comp.OnOffButton(self.generalTab, '', 'WallHack', 200, 130, image='OpenBot/Images/General/wall.tga',funcState=self.WallHackSwich,defaultValue=int(self.wallHack))

		self.redPotButton,self.SlideRedPot,self.redPotLabel = UIComponents.GetSliderButtonLabel(self.generalTab,self.SlideRedMove, '', 'Use Red Potions', 30, 18,image="icon/item/27002.tga",funcState=self.OnRedOnOff,defaultValue=int(self.redPotions),defaultSlider=float(self.minHealth/100.0))
		self.bluePotButton,self.SlideBluePot,self.bluePotLabel = UIComponents.GetSliderButtonLabel(self.generalTab,self.SlideBlueMove, '', 'Use Blue Potions', 30, 50,image="icon/item/27005.tga",funcState=self.OnBlueOnOff,defaultValue=int(self.bluePotions),defaultSlider=float(self.minMana/100.0))
		
		
		##PICKUP
		self.pickupButton,self.SlidePickupSpeed,self.speedPickupLabel = UIComponents.GetSliderButtonLabel(self.pickupTab,self.pickupSpeedSlide, '', 'Enable Pickup', 30, 18,image="OpenBot/Images/General/pickup.tga",funcState=self.OnPickupOnOff,defaultValue=int(self.pickUp),defaultSlider=float(self.pickUpSpeed/3.0))
		self.rangePickupButton,self.SliderangePickup,self.rangePickupLabel = UIComponents.GetSliderButtonLabel(self.pickupTab,self.pickupRangeSlide, 'Range', 'Enable Range Pickup', 15, 60,funcState=self.OnRangePickupOnOff,offsetX=30,offsetY=4,defaultValue=int(self.useRangePickup),defaultSlider=float(self.pickUpRange/10000.0))
		self.ItemValueText = self.comp.TextLine(self.pickupTab, 'Search Item:', 15, 270, self.comp.RGB(255, 255, 255))
		self.SearchPickItemButton = self.comp.Button(self.pickupTab, 'Search', '', 210, 268,  self.UpdatePickFilterList, 'd:/ymir work/ui/public/small_Button_01.sub', 'd:/ymir work/ui/public/small_Button_02.sub', 'd:/ymir work/ui/public/small_Button_03.sub')
		self.AddPickItemBtn = self.comp.Button(self.pickupTab, 'Add Item', '', 200, 170, self.OpenPickItemDialog, 'd:/ymir work/ui/public/Middle_Button_01.sub', 'd:/ymir work/ui/public/Middle_Button_02.sub', 'd:/ymir work/ui/public/Middle_Button_03.sub')
		self.PickCancelBtn = self.comp.Button(self.pickupTab, 'Remove', '', 200, 210, self.UIPickRemoveFilterItem, 'd:/ymir work/ui/public/Middle_Button_01.sub', 'd:/ymir work/ui/public/Middle_Button_02.sub', 'd:/ymir work/ui/public/Middle_Button_03.sub')
		self.PickSearchItemSlotBar, self.PickSearchItemEditLine = self.comp.EditLine(self.pickupTab, '', 85, 270, 110, 15, 20)
		self.labelFilter = self.comp.TextLine(self.pickupTab, 'Pickup Filter', 115, 90, self.comp.RGB(255, 255, 0))
		self.PickfilterModeBtn = self.comp.OnOffButton(self.pickupTab, '\t\t\tExclude Items', 'If not selected will only pick items in the list', 190, 130,funcState=self.OnChangePickMode,defaultValue=int(self.excludeInFilter))
		self.PickbarItems, self.PickfileListBox, self.PickScrollBar = self.comp.ListBoxEx2(self.pickupTab, 15, 117, 140, 150)


		##SHOP
		self.labelSell = self.comp.TextLine(self.shopTab, 'Items to always sell', 95, 10, self.comp.RGB(255, 255, 0))
		self.ShopbarItems, self.ShopFileListBox, self.ShopScrollBar = self.comp.ListBoxEx2(self.shopTab, 60, 30, 140, 150)
		self.AddSellItemBtn = self.comp.Button(self.shopTab, 'Add', '', 65, 185, self.OpenSellItemDialog, 'd:/ymir work/ui/public/Middle_Button_01.sub', 'd:/ymir work/ui/public/Middle_Button_02.sub', 'd:/ymir work/ui/public/Middle_Button_03.sub')
		self.SellRemoveBtn = self.comp.Button(self.shopTab, 'Remove', '', 140, 185, self.UISellRemoveFilterItem, 'd:/ymir work/ui/public/Middle_Button_01.sub', 'd:/ymir work/ui/public/Middle_Button_02.sub', 'd:/ymir work/ui/public/Middle_Button_03.sub')
		#self.BtnRedBuy = self.comp.OnOffButton(self.generalTab, '', 'Buy Red Pots', 200, 130, image='icon/item/27002.tga',funcState=self.OnRedBuy,defaultValue=int(self.wallHack))


		##Init labels
		self.UpdatePickFilterList()
		self.UpdateSellFilterList()
		self.pickupSpeedSlide()
		self.pickupRangeSlide()
		self.SlideRedMove()
		self.SlideBlueMove()

	def LoadSettings(self):
		#OpenLog.DebugPrint("Loading Settings")
		self.autoLogin = boolean(FileManager.ReadConfig("AutoLogin"))
		self.restartHere = boolean(FileManager.ReadConfig("AutoRestart"))
		self.bluePotions = boolean(FileManager.ReadConfig("UseBluePots"))
		self.redPotions = boolean(FileManager.ReadConfig("UseRedPots"))
		self.minMana = int(FileManager.ReadConfig("MinMana"))
		self.minHealth = int(FileManager.ReadConfig("MinHealth"))
		self.pickUp = boolean(FileManager.ReadConfig("PickupUse"))
		self.pickUpRange = int(FileManager.ReadConfig("PickupRange"))
		self.pickUpSpeed = float(FileManager.ReadConfig("PickupSpeed"))
		self.excludeInFilter = boolean(FileManager.ReadConfig("FilterMode"))
		self.useRangePickup = boolean(FileManager.ReadConfig("UseRangePickup"))
		self.wallHack = boolean(FileManager.ReadConfig("WallHack"))
		for i in FileManager.LoadListFile(FileManager.CONFIG_PICKUP_FILTER):
			self.addPickFilterItem(int(i))
		self.sellItems = {int(i) for i in FileManager.LoadListFile(FileManager.CONFIG_SELL_INVENTORY)}

	def SaveSettings(self):
		#OpenLog.DebugPrint("Saving Settings")
		FileManager.WriteConfig("AutoLogin", str(self.autoLogin))
		FileManager.WriteConfig("AutoRestart", str(self.restartHere))
		FileManager.WriteConfig("UseBluePots", str(self.bluePotions))
		FileManager.WriteConfig("UseRedPots", str(self.redPotions))
		FileManager.WriteConfig("MinMana", str(self.minMana))
		FileManager.WriteConfig("MinHealth", str(self.minHealth))
		FileManager.WriteConfig("PickupUse", str(self.pickUp))
		FileManager.WriteConfig("PickupRange", str(self.pickUpRange))
		FileManager.WriteConfig("PickupSpeed", str(self.pickUpSpeed))
		FileManager.WriteConfig("FilterMode", str(self.excludeInFilter))
		FileManager.WriteConfig("UseRangePickup", str(self.useRangePickup))
		FileManager.WriteConfig("WallHack", str(self.wallHack))
		#chat.AppendChat(3,str(self.pickUp))
		FileManager.SaveListFile(FileManager.CONFIG_PICKUP_FILTER,self.pickFilter)
		FileManager.SaveListFile(FileManager.CONFIG_SELL_INVENTORY,self.sellItems)
		FileManager.Save()


#UI STUFF
	def UpdatePickFilterList(self):	
		searchValue = self.PickSearchItemEditLine.GetText()
		self.PickfileListBox.RemoveAllItems()
		for filterItem in sorted(self.pickFilter):
			item.SelectItem(filterItem)
			name = item.GetItemName()
			if searchValue in name:
				self.PickfileListBox.AppendItem(OpenLib.Item(str(filterItem)+" "+name))

	def UpdateSellFilterList(self):
		self.ShopFileListBox.RemoveAllItems()
		for filterItem in sorted(self.sellItems):
			item.SelectItem(filterItem)
			name = item.GetItemName()
			self.ShopFileListBox.AppendItem(OpenLib.Item(str(filterItem)+" "+name))


	def UIAddPickFilterItem(self,item):
		self.addPickFilterItem(item)
		self.UpdatePickFilterList()

	def UIAddSellFilterItem(self,item):
		self.sellItems.add(item)
		self.UpdateSellFilterList()

	def OpenPickItemDialog(self):
		pos = self.Board.GetGlobalPosition()
		ItemListDialog(self.UIAddPickFilterItem,pos[0]+self.Board.GetWidth(),pos[1])
		#ItemListDialog(self.AddFilterItem,pos[0],pos[1])

	
	def OpenSellItemDialog(self):
		pos = self.Board.GetGlobalPosition()
		ItemListDialog(self.UIAddSellFilterItem,pos[0]+self.Board.GetWidth(),pos[1])

	def UISellRemoveFilterItem(self):
		_item = self.ShopFileListBox.GetSelectedItem()
		if _item == None:
			return
		item_name = _item.GetText()
		id = item_name.split(" ",1)
		self.sellItems.remove(int(id))
		self.UpdateSellFilterList()

	def UIPickRemoveFilterItem(self):
		_item = self.PickfileListBox.GetSelectedItem()
		if _item == None:
			return
		item_name = _item.GetText()
		id = item_name.split(" ",1)
		self.delPickFilterItem(int(id[0]))
		self.UpdatePickFilterList()

	def pickupSpeedSlide(self):
		self.pickUpSpeed = round(float(self.SlidePickupSpeed.GetSliderPos()*3),1)
		self.speedPickupLabel.SetText(str('{:,.2f} s'.format(self.pickUpSpeed)))

	def pickupRangeSlide(self):
		self.pickUpRange = int(self.SliderangePickup.GetSliderPos()*10000)
		self.rangePickupLabel.SetText(str(self.pickUpRange))

	def OnRangePickupOnOff(self,val):
		self.useRangePickup = val

	def OnPickupOnOff(self,val):
		self.pickUp = val		

	def ReviveOnOff(self,val):
		self.restartHere = val

	def AutoLoginOnOff(self,val):
		self.autoLogin = val


	def SlideRedMove(self):
		self.minHealth = int(self.SlideRedPot.GetSliderPos()*100)
		self.redPotLabel.SetText(str(self.minHealth))

	def SlideBlueMove(self):
		self.minMana = int(self.SlideBluePot.GetSliderPos()*100)
		self.bluePotLabel.SetText(str(self.minMana))


	def OnRedOnOff(self,val):
		self.redPotions = bool(val)

	def OnBlueOnOff(self,val):
		self.bluePotions = bool(val)
			
		
	#Attack
	def SetOneHand(self): 
		chr.SetMotionMode(chr.MOTION_MODE_ONEHAND_SWORD)

	def SetTwoHand(self): 
		chr.SetMotionMode(chr.MOTION_MODE_TWOHAND_SWORD)
  
	def OpenDmgMenu(self):
		Dmg.switch_state()
	
	#General
	def CheckUsePotions(self):
		val, self.timerPots = OpenLib.timeSleep(self.timerPots,self.TIME_POTS)
		if val:
			if self.redPotions and (float(player.GetStatus(player.HP)) / (float(player.GetStatus(player.MAX_HP))) * 100) < int(self.minHealth):
				OpenLib.UseAnyItemByID(self.RED_POTIONS_IDS)

			if self.bluePotions and (float(player.GetStatus(player.SP)) / (float(player.GetStatus(player.MAX_SP))) * 100) < int(self.minMana):
				OpenLib.UseAnyItemByID(self.BLUE_POTIONS_IDS)

	def checkReviveAndLogin(self):
		val, self.timerDead = OpenLib.timeSleep(self.timerDead,self.TIME_DEAD)

		if not val:
			return

		if self.restartHere and player.GetStatus(player.HP) <= 0:
			OpenLib.Revive()
		
		if self.autoLogin and OpenLib.GetCurrentPhase() == OpenLib.PHASE_LOGIN:
			net.DirectEnter(0,0)
	
	def WallHackSwich(self,val):
		if bool(val):
			self.wallHack = True
			eXLib.DisableCollisions()
		else:
			self.wallHack = False
			eXLib.EnableCollisions()

	#PICKUP
	def OnChangePickMode(self,val):
		self.excludeInFilter = val
		if not val:
			eXLib.ItemGrndOnFilter()
		else:
			eXLib.ItemGrndNotOnFilter()

	def delPickFilterItem(self,id):
		eXLib.ItemGrndDelFilter(id)
		self.pickFilter.remove(int(id))

	def addPickFilterItem(self,id):
		eXLib.ItemGrndAddFilter(id)
		self.pickFilter.add(int(id))
		
	def PickUp(self):
		if self.pickUp:
			val, self.pickUpTimer = OpenLib.timeSleep(self.pickUpTimer,self.pickUpSpeed)
			if not val:
				return
			if OpenLib.GetCurrentPhase() != OpenLib.PHASE_GAME:
				return
			x,y,z = player.GetMainCharacterPosition()
			vid,itemX,itemY = eXLib.GetCloseItemGround(x,y)
			if vid == 0:
				return
			dst = OpenLib.dist(x,y,itemX,itemY)
			allowedRange = max(self.pickUpRange,OpenLib.MAX_PICKUP_DIST) 
			if dst <= allowedRange:
				#Teleport to item
				if dst >= OpenLib.MAX_PICKUP_DIST:
					if not self.useRangePickup:
						return
					Movement.TeleportStraightLine(x,y,itemX,itemY)
					eXLib.SendPickupItem(vid)
					Movement.TeleportStraightLine(itemX,itemY,x,y)
				else:
					eXLib.SendPickupItem(vid)	

	def Close(self):
		self.Board.Hide()
		self.SaveSettings()


	def OnUpdate(self):
		self.CheckUsePotions()
		self.checkReviveAndLogin()
		self.PickUp()

	def switch_state(self):
		if self.Board.IsShow():
			self.Close()
		else:
			self.Board.Show()


class ItemListDialog(ui.Window):

	def __init__(self, onAdd,x,y):
		ui.Window.__init__(self)
		self.Board = ui.BoardWithTitleBar()
		self.Board.SetSize(200, 335)
		self.Board.SetPosition(x, y)
		self.Board.SetTitleName("Item List")
		self.Board.SetCloseEvent(self.Close)
		self.Board.AddFlag("movable")
		self.Board.Show()

		self.onAdd = onAdd
		
		self.comp = UIComponents.Component()
		self.ItemValueText = self.comp.TextLine(self.Board, 'Search Item:', 19, 33, self.comp.RGB(255, 255, 255))
		self.SearchPickItemButton = self.comp.Button(self.Board, 'Search', '', 147, 48,  lambda : self.UpdateFileList(2), 'd:/ymir work/ui/public/small_Button_01.sub', 'd:/ymir work/ui/public/small_Button_02.sub', 'd:/ymir work/ui/public/small_Button_03.sub')
		self.SelectBonus = self.comp.Button(self.Board, 'Add', '', 25, 295, self.addItem, 'd:/ymir work/ui/public/Middle_Button_01.sub', 'd:/ymir work/ui/public/Middle_Button_02.sub', 'd:/ymir work/ui/public/Middle_Button_03.sub')
		self.CancelBonus = self.comp.Button(self.Board, 'Cancel', '', 115, 295, self.Close, 'd:/ymir work/ui/public/Middle_Button_01.sub', 'd:/ymir work/ui/public/Middle_Button_02.sub', 'd:/ymir work/ui/public/Middle_Button_03.sub')
		self.PickSearchItemSlotBar, self.PickSearchItemEditLine = self.comp.EditLine(self.Board, '', 15, 50, 120, 15, 20)
		self.PickfileListBox, self.PickScrollBar = self.comp.FileListBox(self.Board, 15, 80, 180, 200, 10)
	
		self.UpdateFileList(1)

	def addItem(self):
		item = self.PickfileListBox.GetSelectedItem()
		if item == None:
			return None
		item = item.GetText()
		splits = item.split(" ",1)
		self.onAdd(int(splits[0]))
		
	def __del__(self):
		ui.Window.__del__(self)

	def Show(self):
		ui.Window.Show(self)

	def Close(self):
		self.Board.Hide()
		self.__del__()

	def UpdateFileList(self,mode):
		SearchName = str(self.PickSearchItemEditLine.GetText())
		SelectedIndex = self.PickfileListBox.GetSelectedItem()
		self.__RefreshFileList()
		try:
			lines = open(app.GetLocalePath()+"/item_list.txt", "r").readlines()
		except IOError:
			OpenLog.DebugPrint("Load Itemlist Error, you have so set the IDs manually")
			self.Close()
		for line in lines:
			tokens = str(line).split("\t")
			Index = str(tokens[0])
			try:
				Itemname = item.GetItemName(item.SelectItem(int(Index)))
			except Exception:
				continue
			if mode == 1:
				if Index and str(Itemname) != "":
					self.PickfileListBox.AppendItem(OpenLib.Item(Index +"  " + Itemname))
			elif mode == 2:
				if str(Itemname).find(str(SearchName)) != -1:
					self.PickfileListBox.AppendItem(OpenLib.Item(Index +"  " + Itemname))
			elif mode == 3:
				if str(Itemname) == str(SelectedIndex.GetText().split("  ")[1]):
					ItemValue = Index.split("  ")[0]
					self.CreateItemDialog.UpdateItem(int(ItemValue))
					self.Close()
					break

	def __RefreshFileList(self):
		self.PickfileListBox.RemoveAllItems()
		

def GetIDsItemsToSell():
	global instance
	"""
	Returns a set with all items IDs which should be sold.
	Returns:
		[set]: Returns a set with all items which should be sold.
	"""
	return instance.sellItems

def GetSlotItemsToSell():
	global instance
	"""
	Returns a set with all items slots which should be sold.
	Returns:
		[set]: Returns a set with all slots which should be sold.
	"""
	items = instance.sellItems
	slots = set()
	for i in range(0,OpenLib.MAX_INVENTORY_SIZE):
		item = player.GetItemIndex(i)
		if item != 0 and item in items:
			slots.add(i)
	return slots

	

#SettingsDialog().Show()
instance = SettingsDialog()
instance.Show()
def switch_state():
	instance.switch_state()