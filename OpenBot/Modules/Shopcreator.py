import ui,app,chat,chr,net,player,item,skill,time,game,shop,chrmgr,player
import background,constInfo,wndMgr,math,uiCommon,grp,dbg,OpenLib,FileManager,UIComponents
from FileManager import boolean

SHOP_PACKET_ID = 50200 
PREMIUM_SHOP_PACKET_ID = 71221

class ShopDialog(ui.ScriptWindow):
	
	MAX_NUM_SLOT = 40
	MAX_NUM_PREMIUM_SLOT = 80
	
	def __init__(self):
		self.Board = ui.BoardWithTitleBar()
		self.Board.SetTitleName('ShopCreator')
		self.Board.SetPosition(52, 40)
		self.Board.SetSize(350, 500)
		self.Board.AddFlag('movable')
		self.Board.Hide()
		self.Board.SetCloseEvent(self.Hide_UI)
		
		self.comp = UIComponents.Component()
		self.Name = self.comp.TextLine(self.Board, 'Shop-Name:', 30, 440, self.comp.RGB(255, 255, 0))
	
		#self.CloseButton = self.comp.Button(self.Board, '', 'Close', 359, 8, self.Hide_UI, 'd:/ymir work/ui/public/close_button_01.sub', 'd:/ymir work/ui/public/close_button_02.sub', 'd:/ymir work/ui/public/close_button_03.sub')
		self.MultiplicationButton = self.comp.OnOffButton(self.Board, '   Multiply', 'If selected, price will be multiplied by number of items', 250, 440)
		self.MakeShopButton = self.comp.Button(self.Board, 'Make Shop', '', 130, 470, self.CreateShop, 'd:/ymir work/ui/public/large_button_01.sub', 'd:/ymir work/ui/public/large_button_02.sub','d:/ymir work/ui/public/large_button_03.sub')
		self.ShopNameSlotbar, self.ShopNameEditline = self.comp.EditLine(self.Board, '', 95, 440, 140, 18, 25)
		
		self.startX = 15
		self.startY = 35

		self.sizeEditLine = 45

		self.stepY = 19
		self.stepX = 170
		self.endY = 400

				
		self.ShopNameEditline.SetText(FileManager.ReadConfig("ShopName"))
		self.MultiplicationButton.SetValue(boolean(FileManager.ReadConfig("Multiplication")))

		self.items_ui = dict()
		self.iniItems = []
		self.ReloadInv()
		

	def ReloadInv(self):
		del self.items_ui
		if OpenLib.GetItemByID(PREMIUM_SHOP_PACKET_ID) != -1:
			self.MAX_NUM_SLOT = self.MAX_NUM_PREMIUM_SLOT
		else:
			self.MAX_NUM_SLOT = 40
		self.items_ui = dict()
		self.currX = self.startX
		self.currY = self.startY

		for i in range(0, self.MAX_NUM_SLOT):
			_id = player.GetItemIndex(i)
			if _id in self.items_ui or _id == 0:
				continue
			val = FileManager.ReadConfig(str(_id),FileManager.CONFIG_SHOP_CREATOR)
			item.SelectItem(_id)
			item_name = item.GetItemName()
			#itemIcon = item.GetIconImageFileName()
			#self.images.append(self.comp.ExpandedImage(self.Board, self.currX, self.currY, str(itemIcon)))

			if val == "":
				val = "0"

			#UI stuff
			self.items_ui[_id] = dict()
			self.items_ui[_id]['items_label'] = self.comp.TextLine(self.Board, item_name, self.currX + self.sizeEditLine + 5, self.currY, self.comp.RGB(0, 229, 650))
			slot,price = self.comp.EditLine(self.Board, val, self.currX, self.currY, self.sizeEditLine, 15,10)
			self.items_ui[_id]['item_price'] = price
			self.items_ui[_id]['item_slot'] = slot


			self.currY += self.stepY

			if(self.currY>self.endY):
				self.currY = self.startY
				self.currX += self.stepX
		

	def Shopw_UI(self):
		self.Board.Show()
		
	def Hide_UI(self):
		self.Board.Hide()
		for item in self.items_ui:
			FileManager.WriteConfig(str(item),str(self.items_ui[item]['item_price'].GetText()),FileManager.CONFIG_SHOP_CREATOR)
		FileManager.Save(FileManager.CONFIG_SHOP_CREATOR)
		
		FileManager.WriteConfig("ShopName", str(self.ShopNameEditline.GetText()))
		FileManager.WriteConfig("Multiplication", str(self.MultiplicationButton.isOn))
		FileManager.Save()

	#Put item in shop
	def SetItemPrice(self,slot):
		_id = player.GetItemIndex(slot)
		if _id == 0:
			return

		str_price = self.items_ui[_id]['item_price'].GetText()

		if self.MultiplicationButton.isOn:
			won,yang = OpenLib.ConvertPrice(str_price,player.GetItemCount(slot))
		else:
			won,yang = OpenLib.ConvertPrice(str_price,1)

		#Ignore items with price at 0
		if won + yang <= 0.9: 
			return

		shop.AddPrivateShopItemStock(player.SLOT_TYPE_INVENTORY,slot,slot,yang,won)

		
	
	def CreateShop(self):
		if OpenLib.GetItemByID(SHOP_PACKET_ID) == -1:
			chat.AppendChat(3,"[Shop-Creator] You need to buy a packet first.")
			return

		self.iniItems = []
		self.initItems = list(self.items_ui.keys())
		blocked_slots = set() #Avoid selecting the same item twice

		for i in range(0, self.MAX_NUM_SLOT):
			idx = player.GetItemIndex(i)
			if idx == SHOP_PACKET_ID or idx == PREMIUM_SHOP_PACKET_ID or idx == 0:
				continue
			if i in blocked_slots:
				continue
			item.SelectItem(idx)
			size = item.GetItemSize()[0]*item.GetItemSize()[1]
			if size >1:
				for ii in range(1,size):
					blocked_slots.add(i+ii*5)
			#if ItemValue == 50300:
			#	ItemValue = 100000 + player.GetItemMetinSocket(i, 0)
			#if ItemValue != 0:
			self.SetItemPrice(i)
		shop.BuildPrivateShop(self.ShopNameEditline.GetText())


_shop = ShopDialog()

def switch_state():
	if _shop.Board.IsShow():
		_shop.Hide_UI()
	else:
		_shop.ReloadInv()
		_shop.Shopw_UI()