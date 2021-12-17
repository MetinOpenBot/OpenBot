import ui,chat,net,player,item,shop,FileManager,OpenLog, Data
import uiCommon,OpenLib,math,UIComponents


"""
Module responsible for inventory operations.
It also contains the inventory manager window.
ATTENTION: For buy and sell operations make sure the player has a shop open!.
"""


class InventoryDialog(ui.ScriptWindow):

	TIME_WAIT = 1.1

	def __init__(self):
		ui.ScriptWindow.__init__(self)
		self.Board = ui.BoardWithTitleBar()
		self.Board.SetSize(210, 460)
		self.Board.SetPosition(52, 40)
		self.Board.SetTitleName('Inventory Manager')
		self.Board.AddFlag('movable')
		self.Board.SetCloseEvent(self.Board.Hide)
		
		self.comp = UIComponents.Component()
		self.ListBoxLabel = self.comp.TextLine(self.Board, ' Slot:	 ID:			Name:', 8, 33, self.comp.RGB(0, 229, 650))
		self.UpgradeLabel = self.comp.TextLine(self.Board, 'Upgrade			x', 70, 308, self.comp.RGB(255, 255, 255))
		
		#self.Close = self.comp.Button(self.Board, '', 'Close', 188, 7, self.Board.Hide, 'd:/ymir work/ui/public/close_button_01.sub', 'd:/ymir work/ui/public/close_button_02.sub', 'd:/ymir work/ui/public/close_button_03.sub')
		self.Refresh = self.comp.Button(self.Board, '', 'Refresh', 163, 7, self.UpdateFileList, 'd:/ymir work/ui/game/guild/refresh_button_01.sub', 'd:/ymir work/ui/game/guild/refresh_button_02.sub', 'd:/ymir work/ui/game/guild/refresh_button_03.sub')
		self.UpgradeButton = self.comp.Button(self.Board, 'Upgrade', '', 110, 280, self.Upgrade, 'd:/ymir work/ui/public/Large_button_01.sub', 'd:/ymir work/ui/public/Large_button_02.sub','d:/ymir work/ui/public/Large_button_03.sub')
		self.DropSelectedButton = self.comp.Button(self.Board, 'Drop Selected', 'Drops all same Items like the selected one', 110, 358, self.DropItemSelected, 'd:/ymir work/ui/public/Large_button_01.sub', 'd:/ymir work/ui/public/Large_button_02.sub','d:/ymir work/ui/public/Large_button_03.sub')
		self.DropAllButton = self.comp.Button(self.Board, 'Drop All', 'Drops ALL Items in your Inventory', 110, 333, self.DropAllItemsRequest, 'd:/ymir work/ui/public/Large_button_01.sub', 'd:/ymir work/ui/public/Large_button_02.sub','d:/ymir work/ui/public/Large_button_03.sub')
		self.SellSelectedButton = self.comp.Button(self.Board, 'Sell Selected', 'Sells all same Items like the selected one', 15, 358, self.SellItemSelected, 'd:/ymir work/ui/public/Large_button_01.sub', 'd:/ymir work/ui/public/Large_button_02.sub','d:/ymir work/ui/public/Large_button_03.sub')
		self.SellAllButton = self.comp.Button(self.Board, 'Sell All', 'Sells ALL Items in your Inventory', 15, 333, self.SellAllItemsRequest, 'd:/ymir work/ui/public/Large_button_01.sub', 'd:/ymir work/ui/public/Large_button_02.sub','d:/ymir work/ui/public/Large_button_03.sub')
		self.UpgradeSlotbar, self.UpgradeEditline = self.comp.EditLine(self.Board, '1', 112, 307, 15, 18, 1)
		self.BarItems, self.ListBoxItems, ScrollItems = self.comp.ListBoxEx(self.Board, 10, 50, 170, 220)
		self.ModeCombo = self.comp.ComboBox(self.Board, 'Normal', 20, 282, 70)
		self.DropAllSelButton = self.comp.Button(self.Board, 'Drop All Selected', 'Drop items with same ID', 110, 383, self.DropAllItemsSelected, 'd:/ymir work/ui/public/Large_button_01.sub', 'd:/ymir work/ui/public/Large_button_02.sub','d:/ymir work/ui/public/Large_button_03.sub')
		self.SellAllSelButton = self.comp.Button(self.Board, 'Sell All Selected', 'Sell items with same ID', 15, 383, self.SellAllItemsSelected, 'd:/ymir work/ui/public/Large_button_01.sub', 'd:/ymir work/ui/public/Large_button_02.sub','d:/ymir work/ui/public/Large_button_03.sub')
		self.autoSortButton = self.comp.Button(self.Board, 'Sort (Bugged)', 'Sort Inventory', 110, 423, self.Sort, 'd:/ymir work/ui/public/Large_button_01.sub', 'd:/ymir work/ui/public/Large_button_02.sub','d:/ymir work/ui/public/Large_button_03.sub')
		self.stackButton = self.comp.Button(self.Board, 'Stack', 'Stack Items', 15, 423, self.StackItems, 'd:/ymir work/ui/public/Large_button_01.sub', 'd:/ymir work/ui/public/Large_button_02.sub','d:/ymir work/ui/public/Large_button_03.sub')
		UppModes = ['Normal', 'DT', 'Guild', 'Bless', 'Metal', 'Normal - All']
		for Mode in UppModes:
			self.ModeCombo.InsertItem(0, Mode)
		self.UpgradeEditline.SetNumberMode()
		Data.time_InventoryManager_lasttime = 0

		self.toSellSlots = []
		self.toDropSlots = []
		self.toBuySlots = []

		self.toSortMoveActions = []
		self.toStackMoveActions = []

		
		self.callback = None
		self.UpdateFileList()
		
	def switch_state(self):
		if self.Board.IsShow():
			self.Board.Hide()
			self.Hide()
		else:
			self.Board.Show()
			self.UpdateFileList()
			self.Show()
			self.SegiID = int(FileManager.ReadConfig("Blessing-Scroll"))
			self.MetalID = int(FileManager.ReadConfig("Magic-Stone"))

	#Sets a callback that will be called when everything finishes
	def addCallback(self,callback):
		self.callback = callback
		
	def UpdateFileList(self):
		self.ListBoxItems.RemoveAllItems()
		for i in xrange(100):
			ItemIndex = player.GetItemIndex(i)
			if ItemIndex != 0:
				ItemName = item.GetItemName(item.SelectItem(int(ItemIndex)))
				self.ListBoxItems.AppendItem(OpenLib.Item(str(i) + '    ' + str(player.GetItemIndex(i)) + '    ' + ItemName))
				
	def Upgrade(self):
		ItemIndex = self.ListBoxItems.GetSelectedItem()
		SelectedIndex = None
		if ItemIndex:
			SelectedIndex = self.ListBoxItems.GetItemIndex(ItemIndex)
		else:
			chat.AppendChat(7, "[Inv-Manager] No Item selected!")
			return
		try:
			SearchedName = ItemIndex.GetText().split("    ")[2].split("+")[0]
		except:
			SearchedName = ItemIndex.GetText().split("    ")[2]
		
		SelectedItem = ItemIndex.GetText().split("    ")
		count = int(self.UpgradeEditline.GetText())
	
		if self.ModeCombo.GetCurrentText() == 'Normal':
			self.UpgradeItem(1,int(SelectedItem[0]), int(count))
		elif self.ModeCombo.GetCurrentText() == 'DT':
			self.UpgradeItem(2,int(SelectedItem[0]), int(count))
		elif self.ModeCombo.GetCurrentText() == 'Guild':
			self.UpgradeItem(3,int(SelectedItem[0]), int(count))
		elif self.ModeCombo.GetCurrentText() == 'Bless':
			self.UpgradeItem(4,int(SelectedItem[0]), int(count))
		elif self.ModeCombo.GetCurrentText() == 'Normal - All':
			for j in xrange(0, 90):
				ItemValue = player.GetItemIndex(j)
				try:
					ItemName = item.GetItemName(item.SelectItem(ItemValue)).split("+")[0]
				except:
					ItemName = item.GetItemName(item.SelectItem(ItemValue))
				if ItemName == SearchedName:
					self.UpgradeItem(1, j, int(count))
		elif self.ModeCombo.GetCurrentText() == 'Metal':
			self.UpgradeItem(5,int(SelectedItem[0]), int(count))
		if SelectedIndex != None:
			self.ListBoxItems.SelectIndex(SelectedIndex)
	
	def UpgradeItem(self, Mode, Slot, Count):
		self.BannedSlotIndex = []
		for i in xrange(Count):
			if Mode == 1:
				net.SendRefinePacket(Slot, 0)
			elif Mode == 2:
				net.SendRefinePacket(Slot, 4)
			elif Mode == 3:
				net.SendRefinePacket(Slot, 1)
			elif Mode == 4 or Mode == 5:
				for InventorySlot in xrange(player.INVENTORY_PAGE_SIZE*2):
					ItemValue = player.GetItemIndex(InventorySlot)
					if Mode == 4:
						if ItemValue == self.SegiID and not InventorySlot in self.BannedSlotIndex:
							self.BannedSlotIndex.append(InventorySlot)
							net.SendItemUseToItemPacket(InventorySlot, Slot)
							net.SendRefinePacket(Slot, 2)
							break
					elif Mode == 5:	
						if ItemValue == self.MetalID and not InventorySlot in self.BannedSlotIndex:
							self.BannedSlotIndex.append(InventorySlot)
							net.SendItemUseToItemPacket(InventorySlot, Slot)
							net.SendRefinePacket(Slot, 2)
							break
		self.UpdateFileList()
						
	def SellItemSelected(self):
		if not shop.IsOpen():
			chat.AppendChat(7, "[Inv-Manager] You need an open Shop for that!")
			return
		ItemIndex = self.ListBoxItems.GetSelectedItem()
		if ItemIndex:
			pass
		else:
			chat.AppendChat(7, "[Inv-Manager] No selected Items!")
			return
		SelectedItem = ItemIndex.GetText().split("    ")
		self.toSellSlots.append((int(SelectedItem[0]),player.GetItemCount(0),1))
		self.UpdateFileList()
		
	def DropItemSelected(self):
		ItemIndex = self.ListBoxItems.GetSelectedItem()
		if ItemIndex:
			pass
		else:
			chat.AppendChat(7, "[Inv-Manager] No selected Items!")
			return
		SelectedItem = ItemIndex.GetText().split("    ")
		slot = int(SelectedItem[0])
		self.toSellSlots.append(slot,player.GetItemCount(slot))
		self.UpdateFileList()

	def SellAllItemsRequest(self):
		if not shop.IsOpen():
			chat.AppendChat(7, "[Inv-Manager] You need an open Shop for that!")
			return 
		self.QuestionDialog = uiCommon.QuestionDialog()
		self.QuestionDialog.SetText("Do you want so sell All your Items?")
		self.QuestionDialog.SetAcceptEvent(ui.__mem_func__(self.SellAll))
		self.QuestionDialog.SetCancelEvent(ui.__mem_func__(self.CancelQuestionDialog))
		self.QuestionDialog.Open()

	def SellAll(self):
		for i in range(0,OpenLib.MAX_INVENTORY_SIZE):
			idx = player.GetItemIndex(i)
			if idx != 0:
				self.toSellSlots.append(i)
		self.CancelQuestionDialog()
		self.UpdateFileList()
		
	def DropAllItemsRequest(self):
		self.QuestionDialog = uiCommon.QuestionDialog()
		self.QuestionDialog.SetText("Do you want to drop ALL your Items?")
		self.QuestionDialog.SetAcceptEvent(ui.__mem_func__(self.DropAll))
		self.QuestionDialog.SetCancelEvent(ui.__mem_func__(self.CancelQuestionDialog))
		self.QuestionDialog.Open()

	def DropAll(self):
		for i in range(0,OpenLib.MAX_INVENTORY_SIZE):
			idx = player.GetItemIndex(i)
			if idx != 0:
				self.toDropSlots.append(i)
		self.CancelQuestionDialog()
		self.UpdateFileList()
		
	def CancelQuestionDialog(self):
		self.QuestionDialog.Close()
		self.QuestionDialog = None

	def DropAllItemsSelected(self):

		ItemIndex = self.ListBoxItems.GetSelectedItem()
		if ItemIndex:
			pass
		else:
			chat.AppendChat(7, "[Inv-Manager] No selected Items!")
			return
		SelectedItem = ItemIndex.GetText().split("    ")
		selIdx = int(SelectedItem[1])

		for i in range(0,OpenLib.MAX_INVENTORY_SIZE):
			idx = player.GetItemIndex(i)
			if idx != 0 and idx == selIdx:
				self.toDropSlots.append(i)

	def SellAllItemsSelected(self):
		if not shop.IsOpen():
			chat.AppendChat(7, "[Inv-Manager] You need an open Shop for that!")
			return
		ItemIndex = self.ListBoxItems.GetSelectedItem()
		if ItemIndex:
			pass
		else:
			chat.AppendChat(7, "[Inv-Manager] No selected Items!")
			return
		SelectedItem = ItemIndex.GetText().split("    ")
		selIdx = int(SelectedItem[1])

		for i in range(0,OpenLib.MAX_INVENTORY_SIZE):
			idx = player.GetItemIndex(i)
			if idx != 0 and idx == selIdx:
				self.toSellSlots.append(i)

	def StackItems(self):
		items_arr = dict()
		self.toStackMoveActions = []
		for i in range(0,OpenLib.MAX_INVENTORY_SIZE):
			idx = player.GetItemIndex(i)
			if idx != 0:
				if idx not in items_arr:
					items_arr[idx] = [player.GetItemCount(i),i]
					continue
					
				
				count = player.GetItemCount(i)
				total_sum = count + items_arr[idx][0]
				if total_sum < OpenLib.MAX_ITEM_COUNT:
					items_arr[idx][0] = total_sum
					self.toStackMoveActions.append((i,items_arr[idx][1],count))
				else:
					excess = total_sum - OpenLib.MAX_ITEM_COUNT
					self.toStackMoveActions.append((i,items_arr[idx][1],count - excess))
					items_arr[idx][0] = excess
					items_arr[idx][1] = i

	def Sort(self):
		algo = SortAlgorithm()
		self.toSortMoveActions = []
		self.toSortMoveActions = algo.sort()
		OpenLog.DebugPrint("[SORT] - Number of actions to be processed: "+str(len(self.toSortMoveActions)))

	def OnUpdate(self):
		val, Data.time_InventoryManager_lasttime = OpenLib.timeSleep(Data.time_InventoryManager_lasttime,self.TIME_WAIT)
		if val:
			if len(self.toDropSlots) > 0:
				slot = self.toDropSlots.pop(0)
				net.SendItemDropPacketNew(slot,player.GetItemCount(slot))
				return
			if len(self.toSellSlots) > 0:
				slot = self.toSellSlots.pop(0)
				net.SendShopSellPacketNew(slot,player.GetItemCount(slot),1)
				return

			if len(self.toStackMoveActions) > 0:
				args = self.toStackMoveActions.pop(0)
				OpenLog.DebugPrint("[STACK] - Changing item position from "+ str(args[0]) + " to " + str(args[1]) + " count " + str(args[2]))
				net.SendItemMovePacket(args[0],args[1],args[2])
				return

			if len(self.toSortMoveActions) > 0:
				args = self.toSortMoveActions.pop(0)
				OpenLog.DebugPrint("[SORT] - Changing item position from "+ str(args[0]) + " to " + str(args[1]) + " count " + str(args[2]))
				net.SendItemMovePacket(args[0],args[1],args[2])
				return

			if len(self.toBuySlots) > 0:
				slot= self.toBuySlots.pop(0)
				net.SendShopBuyPacket(slot)
				return

			if self.callback != None:
				self.callback()
				self.callback = None

	def unStackItem(self, item_slot, item_slot_destination, item_count):
		if OpenLib.isInventoryFull():
			net.SendItemMovePacket(item_slot, item_slot_destination, item_count)
		else:
			chat.AppendChat(3, '[InventoryManager] You have less than 10 free spaces in inventory, unstackin cannot be done')

###################SORT SCRIPT#######################
# It has some bugs
######BUGGED########
#By radu97 (https://m2bob-forum.net/index.php/Thread/56396-RELEASE-Inventory-Sorter/?pageNo=1)
SLOTS = OpenLib.MAX_INVENTORY_SIZE
SLOTS_PER_PAGE = 2#player.INVENTORY_PAGE_SIZE
	  
class Item:
	def __init__(self, id, slot, size, name):
		self.id = id
		self.slot = slot
		self.size = size
		self.name = name
	def move(self, slot):
		OpenLog.DebugPrint("===> The item " + str(self.name) + " has been moved to slot " + str(slot))
		#net.SendItemMovePacket(self.slot, slot, 0)
		self.slot = slot
		
class SortAlgorithm:
	def __init__(self):
		self.list = []
		self.placed = []
	
	def retrieveItems(self):
		OpenLog.DebugPrint("========= Retrieving item list ==========")
		
		for slot in range(SLOTS):
			item_id = player.GetItemIndex(slot)
			if item_id != 0:
				item.SelectItem(item_id)
				self.list.append(Item(item_id, slot, int(item.GetItemSize()[1]), item.GetItemName()))
		
		OpenLog.DebugPrint("========= Retrieving successful ==========")
				
	def sortByID(self):
		chat.AppendChat(3, "========= Sorting items by ID ==========")
		
		self.list.sort(key=lambda item: item.id, reverse=False)
		
		OpenLog.DebugPrint("========= Sorting successful ==========")
		
	def sortByName(self):
		chat.AppendChat(3, "========= Sorting items by NAME ==========")
		
		self.list.sort(key=lambda item: item.name, reverse=False)
		
		OpenLog.DebugPrint("========= Sorting successful ==========")
		
	def sortBySizeAndID(self):
		chat.AppendChat(3, "========= Sorting items by NAME ==========")
		
		self.list.sort(key=lambda item: (-item.size, item.id), reverse=False)
		
		OpenLog.DebugPrint("========= Sorting successful ==========")
	
	def sortBySizeReversed(self):
		chat.AppendChat(3, "========= Sorting items by NAME ==========")
		
		self.list.sort(key=lambda item: item.size, reverse=False)
		
		OpenLog.DebugPrint("========= Sorting successful ==========")
		
	def getNextSlot(self, size):
		for page in range(int(math.ceil(SLOTS / SLOTS_PER_PAGE))):
			LAST_SLOT_THIS_PAGE = min((page + 1) * SLOTS_PER_PAGE, SLOTS)
			for slot in range(page * SLOTS_PER_PAGE, LAST_SLOT_THIS_PAGE):
				if slot + 5 * (size - 1) < LAST_SLOT_THIS_PAGE:
					good = True
					
					for i in range(size):
						if (slot + 5 * i) in self.placed:
							good = False
					
					if good:
						OpenLog.DebugPrint("===> Best slot found is " + str(slot))
						return slot
		
		OpenLog.DebugPrint("===> No free slots found of size " + str(size))
		return -1
		
	def itemsInSlot(self, slot, size):
		items = []
		for i in range(size):
			cur_slot = slot + i * 5
			it = [x for x in self.list if x.slot == cur_slot or (x.size == 2 and x.slot + 5 == cur_slot or False) or (x.size == 3 and (x.slot + 10 == cur_slot or x.slot + 5 == cur_slot) or False) ]
			
			if len(it) > 0 and it[0] not in items:
				OpenLog.DebugPrint("=====> The item " + str(it[0].name) + " is in the way" + str(size))
				items.append(it[0])
		
		return items
	
	def getNextFreeSlot(self, size, skip = []):
		for page in range(int(math.ceil(SLOTS / SLOTS_PER_PAGE))):
			LAST_SLOT_THIS_PAGE = min((page + 1) * SLOTS_PER_PAGE, SLOTS)
			for slot in range(page * SLOTS_PER_PAGE, LAST_SLOT_THIS_PAGE):
				if slot not in skip and len(self.itemsInSlot(slot, size)) == 0 and slot + 5 * (size - 1) < LAST_SLOT_THIS_PAGE:
					return slot
		
		OpenLog.DebugPrint("Could not find any free slot")
		return -1        
	def setItemAsPlaced(self, item):
		OpenLog.DebugPrint("===> The item has been placed in the right slot")
		for i in range(item.size):
			self.placed.append(item.slot + 5 * i)
	
	def sort(self,sortBy=3):
		movement_list = []
		self.retrieveItems()
		
		if sortBy == 1:
			self.sortByID()
		elif sortBy == 2:
			self.sortByName()
		elif sortBy == 3:
			self.sortBySizeAndID()
		else:
			self.sortBySizeReversed()
		
		for it in self.list:
			for z in range(1000):
				continue
			OpenLog.DebugPrint("Sorting Item " + str(it.name))
			
			next_slot = self.getNextSlot(it.size)
			
			if next_slot == -1:
				continue
			
			if it.slot == next_slot:
				self.setItemAsPlaced(it)
				continue
			
			occupied_slots = []
			
			for i in range(it.slot):
				occupied_slots.append(next_slot + 5 * i)
			
			for in_way_item in self.itemsInSlot(next_slot, it.size):
				next_free_slot = self.getNextFreeSlot(in_way_item.size, occupied_slots)
				
				if next_free_slot == -1:
					continue
					
				in_way_item.move(next_free_slot)
				
			movement_list.append((it.slot, next_slot, 0))
			it.move(next_slot)
			self.setItemAsPlaced(it)
		return movement_list

	
inv = InventoryDialog()
inv.Show()

def switch_state():
	inv.switch_state()