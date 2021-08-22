import ui
import OpenLib,eXLib,UIComponents

class FilterDialog(ui.Window):
	def __init__(self):
		ui.Window.__init__(self)
		self.BuildWindow()

	def __del__(self):
		ui.Window.__del__(self)

	def BuildWindow(self):
		self.Board = ui.BoardWithTitleBar()
		self.Board.SetSize(235, 350)
		self.Board.SetCenterPosition()
		self.Board.AddFlag('movable')
		self.Board.AddFlag('float')
		self.Board.SetTitleName('Packet Filter')
		self.Board.SetCloseEvent(self.Close)
		self.Board.Hide()
		self.comp = UIComponents.Component()

		self.inBoard = self.comp.ThinBoard(self.Board, False, 18, 47, 80, 132, False)
		self.outBoard = self.comp.ThinBoard(self.Board, False, 126, 47, 81, 134, False)
		self.start_stopBtn = self.comp.OnOffButton(self.Board, '', '', 95, 300,funcState=self.start_stop ,OffUpVisual='OpenBot/Images/start_0.tga', OffOverVisual='OpenBot/Images/start_1.tga', OffDownVisual='OpenBot/Images/start_2.tga',OnUpVisual='OpenBot/Images/stop_0.tga', OnOverVisual='OpenBot/Images/stop_1.tga', OnDownVisual='OpenBot/Images/stop_2.tga',defaultValue=False )
		self.outboundBtn = self.comp.Button(self.Board, 'Add', '', 167, 187, self.addOutBound, 'd:/ymir work/ui/public/small_button_01.sub', 'd:/ymir work/ui/public/small_button_02.sub', 'd:/ymir work/ui/public/small_button_03.sub')
		self.inboundBtn = self.comp.Button(self.Board, 'Add', '', 58, 187, self.addInBound, 'd:/ymir work/ui/public/small_button_01.sub', 'd:/ymir work/ui/public/small_button_02.sub', 'd:/ymir work/ui/public/small_button_03.sub')
		self.removeBtnOutBound = self.comp.Button(self.Board, 'Remove', '', 18, 212, self.removeInbound, 'd:/ymir work/ui/public/large_button_01.sub', 'd:/ymir work/ui/public/large_button_02.sub', 'd:/ymir work/ui/public/large_button_03.sub')
		self.removeBtnInbound = self.comp.Button(self.Board, 'Remove', '', 126, 212, self.removeOutbound, 'd:/ymir work/ui/public/large_button_01.sub', 'd:/ymir work/ui/public/large_button_02.sub', 'd:/ymir work/ui/public/large_button_03.sub')
		self.clearBtnOutBound = self.comp.Button(self.Board, 'Clear', '', 18, 237, self.clearOutbound, 'd:/ymir work/ui/public/small_button_01.sub', 'd:/ymir work/ui/public/small_button_02.sub', 'd:/ymir work/ui/public/small_button_03.sub')
		self.clearBtnInbound = self.comp.Button(self.Board, 'Clear', '', 126, 237, self.clearInbound, 'd:/ymir work/ui/public/small_button_01.sub', 'd:/ymir work/ui/public/small_button_02.sub', 'd:/ymir work/ui/public/small_button_03.sub')
		self.inboundModeBtn = self.comp.OnOffButton(self.Board, 'Mode', 'If set, will only show packets in the list', 62, 237,funcState=self.inboundMode)
		self.outboundModeBtn = self.comp.OnOffButton(self.Board, 'Mode', 'If set, will only show packets in the list', 169, 237,funcState=self.outboundMode)
		self.slotbar_inHeader, self.inHeaderEditBox = self.comp.EditLine(self.Board, '0', 18, 187, 25, 15, 3)
		self.slotbar_outHeader, self.outHeaderEditBox = self.comp.EditLine(self.Board, '0', 126, 187, 25, 15, 3)
		self.clearConsoleBtn = self.comp.Button(self.Board, 'Clear Console', '', 67, 272, self.clearConsole, 'd:/ymir work/ui/public/large_button_01.sub', 'd:/ymir work/ui/public/large_button_02.sub', 'd:/ymir work/ui/public/large_button_03.sub')
		#self.nameinboundMode = self.comp.TextLine(self.Board, 'Mode', 18, 262)
		#self.nameOutgoingMode = self.comp.TextLine(self.Board, 'Mode', 126, 262)
		self.nameINcome = self.comp.TextLine(self.Board, 'Incomming Filter', 21, 29, self.comp.RGB(66, 255, 87))
		self.nameOutgoing = self.comp.TextLine(self.Board, 'Outgoing Filter', 132, 28, self.comp.RGB(62, 255, 87))
		self.bar_inbFilter, self.list_inbFilter, self.scroll_1= self.comp.ListBoxEx(self.Board, 23, 53, 70, 121)
		self.bar_outbFilter, self.list_outbFilter, self.scroll_2 = self.comp.ListBoxEx(self.Board, 132, 52, 69, 123)
		self.list_inbFilter.SetViewItemCount(6)
		self.list_outbFilter.SetViewItemCount(6)
		self.inboundModeBtn.SetOff()
		self.outboundModeBtn.SetOff()
		#example: self.list_xxx.AppendItem(Item('text 1'))


	def inboundMode(self,val):
		eXLib.SetInFilterMode(val)
	def outboundMode(self,val):
		eXLib.SetOutFilterMode(val)

	def start_stop(self,val):
		if(val):
			eXLib.StartPacketFilter()
		else:
			eXLib.StopPacketFilter()
	
	def clearConsole(self):
		eXLib.ClearOutput()

	def addOutBound(self):
		header = self.outHeaderEditBox.GetText()
		eXLib.SkipOutHeader(int(header))
		self.list_outbFilter.AppendItem(OpenLib.Item(header))
	
	def addInBound(self):
		header = self.inHeaderEditBox.GetText()
		eXLib.SkipInHeader(int(header))
		self.list_inbFilter.AppendItem(OpenLib.Item(header))
	
	def removeInbound(self):
		item = self.list_inbFilter.GetSelectedItem()
		headerNum = item.GetText()
		eXLib.DoNotSkipInHeader(int(headerNum))
		self.list_inbFilter.RemoveItem(item)
	
	def removeOutbound(self):
		item = self.list_outbFilter.GetSelectedItem()
		headerNum = item.GetText()
		eXLib.DoNotSkipOutHeader(int(headerNum))
		self.list_outbFilter.RemoveItem(item)
	
	def clearInbound(self):
		eXLib.ClearInFilter()
		for item in self.list_inbFilter.itemList:
			self.list_inbFilter.RemoveItem(item)


	def clearOutbound(self):
		eXLib.ClearOutFilter()
		for item in self.list_outbFilter.itemList:
			self.list_outbFilter.RemoveItem(item)

	def Show(self):
		self.Board.Show()
		self.clearInbound()
		self.clearOutbound()
		eXLib.LaunchPacketFilter()


	def switch_state(self):
		if self.Board.IsShow():
			self.Close()
		else:
			self.Show()
	
	
	def OnKeyDown(self, key):
		try:
			self.onPressKeyDict[key]()
		except KeyError:
			pass
		except:
			raise
		return True
	
	def OpenWindow(self):
		if self.Board.IsShow():
			self.Board.Hide()
		else:
			self.Board.Show()
	
	def Close(self):
		eXLib.ClosePacketFilter()
		self.Board.Hide()


dialog = FilterDialog()
dialog.Show()
