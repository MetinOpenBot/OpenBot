import ui,app,chr,net,player,item,skill,time,game,shop,thread,chat,eXLib,OpenLib,Movement
import UIComponents

BOARD_SIZE_X = 300
BOARD_SIZE_Y = 450


def convertPrice(money,won=0):
	num = 0
	_money = money+won*100000000
	while _money>=1000:
		_money = _money/1000
		num+=1
	_str ='k'
	_money="{0:0.1f}".format(_money)
	return str(_money) + str(_str*num)


def relativeEndY(Y_value):
	return BOARD_SIZE_Y - abs(Y_value)

def relativeEndX(X_value):
	return BOARD_SIZE_X - abs(X_value)

def relativeCenterY(Y_value):
	return BOARD_SIZE_Y/2 + Y_value

def relativeCenterX(X_value):
	return BOARD_SIZE_X/2 + X_value

#Called when new shop appears
def shopCallback(vid):
	if(searchDialog.State != 0):	
		searchDialog.PlayersVids.append(vid)

class SearchDialog(ui.ScriptWindow):

	SLOT_COUNT = 40
	STATE_OPEN_SHOP = 1
	STATE_WAIT_SHOP_OPEN = 2
	STATE_WAIT_SHOP_CLOSE = 3
	Items = []
	ATTEMPTS_WAIT = 2
	numAttempts = 0
	TIME_WAIT = 0.25
 
	lastTime = 0
 
 
	class ListItem(ui.ListBoxEx.Item):
		def __init__(self, item):
			ui.ListBoxEx.Item.__init__(self)
			self.canLoad=0
			self.item=item
			self.textLine=self.__CreateTextLine(item.GetDisplay())          

		def __del__(self):
			ui.ListBoxEx.Item.__del__(self)

		def GetText(self):
			return self.item

		def SetSize(self, width, height):
			ui.ListBoxEx.Item.SetSize(self, 6*len(self.textLine.GetText()) + 4, height)

		def __CreateTextLine(self, fileName):
			textLine=ui.TextLine()
			textLine.SetParent(self)
			textLine.SetPosition(0, 0)
			textLine.SetText(fileName)
			textLine.Show()
			return textLine	

	class Item:
		def __init__(self, itemName, shopVID, count, price, slot, won = 0):
			self.name = itemName
			self.shop = shopVID
			self.count = count
			self.price = (price + won*100000000)/self.count
			self.slot = slot
		def GetDisplay(self):
			return " {:20}     {:10}    {:10}".format(self.name[:20],chr.GetNameByVID(self.shop)[:10], convertPrice(self.price))
		def getStringFormat(self):
			return "Slot: " + str(self.slot) + "  Name: " + str(self.name) + "  Price: " + str(self.price) + " yang  Count: " + str(self.count) + " Shop VID: " + str(self.shop)
	
	def __init__(self):
		self.closeAttempt = 0
		ui.ScriptWindow.__init__(self)
		eXLib.RegisterNewShopCallback(shopCallback)
		
		self.Board = ui.BoardWithTitleBar()
		self.Board.SetTitleName('SearchBot')
		self.Board.SetCloseEvent(self.CloseWindow)
		self.Board.SetSize(BOARD_SIZE_X, BOARD_SIZE_Y)
		self.Board.SetCenterPosition()
		self.Board.AddFlag("movable")
		#self.Board.Show()

		self.comp = UIComponents.Component()
		self.SearchButton = self.comp.OnOffButton(self.Board, '', '', relativeCenterX(-20),relativeEndY(55),funcState=self.EnableButtonClicked, OffUpVisual=eXLib.PATH + 'OpenBot/Images/start_0.tga', OffOverVisual=eXLib.PATH + 'OpenBot/Images/start_1.tga', OffDownVisual=eXLib.PATH + 'OpenBot/Images/start_2.tga',OnUpVisual=eXLib.PATH + 'OpenBot/Images/stop_0.tga', OnOverVisual=eXLib.PATH + 'OpenBot/Images/stop_1.tga', OnDownVisual=eXLib.PATH + 'OpenBot/Images/stop_2.tga' )
		self.SearchButton.SetOff()
		#self.SearchButton = self.comp.ToggleButton(self.Board,'Search Shops','',relativeCenterX(-48),relativeEndY(45),self.StopSearch,self.StartSearch,'d:/ymir work/ui/public/large_button_01.sub', 'd:/ymir work/ui/public/large_button_02.sub', 'd:/ymir work/ui/public/large_button_03.sub')
  
		self.SkillIdNameLabel = self.comp.TextLine(self.Board, 'Item Name		Shop Name		Price', 16, 30, self.comp.RGB(255, 255, 255))
		self.BarItems, self.ListBoxItems, ScrollItems = self.comp.ListBoxEx(self.Board, 10, 45, relativeEndX(42), relativeEndY(205))
		self.ListBoxItems.SetViewItemCount(12)
		
		
		self.ItemEditBoxSlot, self.ItemEditBoxValue= self.comp.EditLine(self.Board,"",15,relativeEndY(-148),relativeEndX(120),14,25)
		self.ItemSubmitButton = self.comp.Button(self.Board, 'Search', 'Search in List',relativeEndX(-100),relativeEndY(150),self.UpdateItemList,'d:/ymir work/ui/public/large_button_01.sub', 'd:/ymir work/ui/public/large_button_02.sub', 'd:/ymir work/ui/public/large_button_03.sub')
		
		#self.DistanceLabel = self.comp.TextLine(self.Board, 'Distance to Shop: ', 16, relativeEndY(35), self.comp.RGB(255, 255, 0))
		#self.DistanceNumber = self.comp.TextLine(self.Board, 'NULL', 100, relativeEndY(35), self.comp.RGB(255, 255, 0))
		self.BuyItemButton = self.comp.Button(self.Board, 'Buy Item', 'Buy selected Item',relativeEndX(-100), relativeEndY(80),self.BuySelectedItem,'d:/ymir work/ui/public/large_button_01.sub', 'd:/ymir work/ui/public/large_button_02.sub', 'd:/ymir work/ui/public/large_button_03.sub')
		self.OpenShopButton = self.comp.Button(self.Board, 'Open Shop', 'Open the selected shop',relativeEndX(-100),relativeEndY(120),self.OpenSelectedShop,'d:/ymir work/ui/public/large_button_01.sub', 'd:/ymir work/ui/public/large_button_02.sub', 'd:/ymir work/ui/public/large_button_03.sub')
		self.MoveShopButton = self.comp.Button(self.Board, 'Move to Shop', 'Move to selected shop',relativeEndX(-100),relativeEndY(100),self.MoveSelectedShop,'d:/ymir work/ui/public/large_button_01.sub', 'd:/ymir work/ui/public/large_button_02.sub', 'd:/ymir work/ui/public/large_button_03.sub')
		
		self.lShopsSearch = self.comp.TextLine(self.Board, '', 14, relativeEndY(100), self.comp.RGB(255, 255, 0))
		self.lShopsToBeSearch = self.comp.TextLine(self.Board, '', 15, relativeEndY(80), self.comp.RGB(255, 255, 0))
		self.lNumItems = self.comp.TextLine(self.Board, '', 14, relativeEndY(120), self.comp.RGB(255, 255, 0))

		self.PlayersVids = []
		self.State = 0
		self.PlayerIndex = 0

	def EnableButtonClicked(self,val):
		if(val):
			self.StartSearch()
		else:
			self.StopSearch()


	def StartSearch(self):
		self.numShopsSearched = 0
		self.State = 1
		self.PlayersVids = []
		self.Items = []
		self.PlayerIndex = 0
		self.ScanPlayers()
		self.State = self.STATE_OPEN_SHOP

	def UpdateLabelText(self):
		self.lShopsSearch.SetText("Shops Searched: " + str(self.numShopsSearched))
		self.lShopsToBeSearch.SetText("Shops To Be Searched: " + str(len(self.PlayersVids)))
		self.lNumItems.SetText("Number of Items: " + str(len(self.Items)))


	def MoveSelectedShop(self):
		itemList = self.ListBoxItems.GetSelectedItem()
		if itemList:
			item = itemList.GetText()
			x,y,z = chr.GetPixelPosition(item.shop)
			chr.MoveToDestPosition(player.GetMainCharacterIndex(),x, y)
	
	def OpenSelectedShop(self):
		itemList = self.ListBoxItems.GetSelectedItem()
		if itemList:
			item = itemList.GetText()
			net.SendOnClickPacket(item.shop)
		
		
	def StopSearch(self):
		self.State = 0
  
	def CloseWindow(self):
		self.Board.Hide()
		self.Board.Destroy()


	def UpdateItemList(self):
		value = self.ItemEditBoxValue.GetText()
		self.ListBoxItems.RemoveAllItems()
		lst = []
		for item in self.Items:
			if value in item.name:
				lst.append(item)
		lst.sort(key=lambda x: x.price)
		for item in lst:
			self.ListBoxItems.AppendItem(self.ListItem(item))
  
	def ScanPlayers(self):
		for x in eXLib.InstancesList:
			test = chr.HasInstance(x)
			chr.SelectInstance(x)
			if test != 0 and chr.GetRace(x) >= OpenLib.MIN_RACE_SHOP and chr.GetRace(x) <= OpenLib.MAX_RACE_SHOP:
				#chat.AppendChat(3,"Name: " + str(chr.GetNameByVID(x)) + " IsShop: " +  str(chr.GetRace(x)))
				self.PlayersVids.append(x)
		self.UpdateLabelText()
		return True

	def BuySelectedItem(self):
		itemList = self.ListBoxItems.GetSelectedItem()
		if itemList:
			item = itemList.GetText()
			self.BuyItemDirectly(item)

	def BuyItemDirectly(self,item):
		vid = item.shop
		slot = item.slot
		x,y,z = player.GetMainCharacterPosition()
		dst_x,dst_y,dst_z = chr.GetPixelPosition(vid)
		if(dst_x + dst_y < 0.000001):
			return
		Movement.TeleportStraightLine(x,y,dst_x,dst_y)
		net.SendOnClickPacket(vid)
		net.SendShopBuyPacket(slot)
		Movement.TeleportStraightLine(dst_x,dst_y,x,y)
		net.SendShopEndPacket()

	def OpenShop(self,vid):
		if self.IsShopOpen() == False and chr.HasInstance(vid):
			net.SendOnClickPacket(vid)

	def IsShopOpen(self):
		return shop.IsOpen()
    
	def CloseShop(self):
		if self.IsShopOpen() == True:
			net.SendShopEndPacket()

	def ScanShop(self,vid):
		self.numShopsSearched+=1
		chr.SelectInstance(vid)
		for x in range(0,self.SLOT_COUNT*shop.GetTabCount()):
			id = shop.GetItemID(x)
			if id != 0:
				price = shop.GetItemPrice(x)
				name = item.GetItemNameByVnum(id)
				if id == 50300:
					sk = shop.GetItemMetinSocket(x,0)
					skill_name = str(skill.GetSkillName(sk))
					name = str(skill_name) + " " + name
				count = shop.GetItemCount(x)
				it = self.Item(name,vid,count,price,x,shop.GetItemCheque(x))
				self.Items.append(it)
		self.UpdateLabelText()
				#chat.AppendChat(3,"Slot: " + str(x) + "  Name: " + str(name) + "  Price: " + str(price) + " yang  Count: " + str(count))
        
	def OnUpdate(self):
		currTime = app.GetTime()
		if currTime-self.lastTime < self.TIME_WAIT:
			return
  
		if self.State == 0:
			return

		self.lastTime = currTime
       
		if self.State == self.STATE_OPEN_SHOP and len(self.PlayersVids)>0:
			self.PlayerVID = self.PlayersVids.pop()
			self.OpenShop(self.PlayerVID)
			self.State = self.STATE_WAIT_SHOP_OPEN
			return
        
		elif self.State == self.STATE_WAIT_SHOP_OPEN:
			#chat.AppendChat(3,"State Wait Open Shop")
			if self.numAttempts > self.ATTEMPTS_WAIT:
				#chat.AppendChat(3,"Skipping Wait Open")
				self.numAttempts = 0
				self.State = self.STATE_WAIT_SHOP_CLOSE
				return
			if self.IsShopOpen() == True:
				self.State = self.STATE_WAIT_SHOP_CLOSE
				self.ScanShop(self.PlayerVID)
				self.CloseShop()
				self.numAttempts = 0
			else:
				self.OpenShop(self.PlayerVID)
				self.numAttempts += 1 
			return
        
		elif self.State == self.STATE_WAIT_SHOP_CLOSE:
			#chat.AppendChat(3,"State Wait Close Shop")
			if self.IsShopOpen() == False:
				self.numAttempts = 0
				self.State = self.STATE_OPEN_SHOP
				return
			else:
				if(self.closeAttempt>3):
					self.closeAttempt = 0
					self.CloseShop()
					return
				self.closeAttempt += 1 
				return
        

def switch_state():
	if searchDialog.Board.IsShow():
		searchDialog.Board.Hide()
		searchDialog.StopSearch()
		searchDialog.SearchButton.SetOff()
	else:
		searchDialog.Board.Show()
	
searchDialog = SearchDialog()
searchDialog.Show()

