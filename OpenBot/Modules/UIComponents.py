import ui

def RGB(r, g, b):
	return (r*255, g*255, b*255)


def GetCurrentText(self):
	return self.textLine.GetText()


def OnSelectItem(self, index, name):
	self.SetCurrentItem(name)
	self.CloseListBox()
	self.event()
	
def GetSelectedIndex(self):
	return self.listBox.GetSelectedItem()

ui.ComboBox.GetCurrentText = GetCurrentText
ui.ComboBox.GetSelectedIndex = GetSelectedIndex
ui.ComboBox.OnSelectItem = OnSelectItem


#func is a callback that give responsabilty to the caller for changing the state
#funcState is a callback that automatically changes the sate and pass it (the new state) as argument
class OnOffButton(ui.Button):
	def __init__(self,OffUpVisual, OffOverVisual, OffDownVisual,OnUpVisual, OnOverVisual, OnDownVisual, image=None,tooltip=None,funcState=None,defaultValue=0):
		defaultValue = bool(defaultValue)
		ui.Button.__init__(self)
		self.OffUpVisual = OffUpVisual
		self.OffOverVisual = OffOverVisual 
		self.OffDownVisual = OffDownVisual
		self.OnUpVisual = OnUpVisual
		self.OnOverVisual = OnOverVisual
		self.OnDownVisual = OnDownVisual
		self.FuncState = funcState
		self.isOn = not defaultValue
		self.ExpandedImage = image 
		self.SetEvent(self.OnChange)
		self.OnChange()

	def OnChange(self):
		if self.isOn == True:
			self.SetOff()
		else:
			self.SetOn()

		if self.FuncState != None:
			self.FuncState(self.isOn)

	def SetValue(self,val):
		if val == 1 or val == True:
			self.SetOn()
		else:
			self.SetOff()

	def SetOn(self):
		self.SetUpVisual(self.OnUpVisual)
		self.SetOverVisual(self.OnOverVisual)
		self.SetDownVisual(self.OnDownVisual)
		self.isOn = True

	def SetOff(self):
		self.SetUpVisual(self.OffUpVisual)
		self.SetOverVisual(self.OffOverVisual)
		self.SetDownVisual(self.OffDownVisual)
		self.isOn = False
	def __del__(self):
		self.Hide()
		if self.image != None:
			self.image.Hide()
			self.image.__del__()
		ui.Button.__del__(self)
	
class SlotWithToolTip(ui.SlotWindow):
	def __init__(self,x,y,vnum,count,slotIndex,parent):
		slot = ui.SlotWindow.__init__(self)
		slot.SetParent(parent)
		slot.SetSize(32, 32)
		slot.SetSlotBaseImage("d:/ymir work/ui/public/Slot_Base.sub", 1.0, 1.0, 1.0, 1.0)
		slot.AppendSlot(slotIndex, 0, 0, 32, 32)
		slot.SetOverInItemEvent(ui.__mem_func__(self.OverInItem))
		slot.SetOverOutItemEvent(ui.__mem_func__(self.OverOutItem))
		slot.SetPosition(x, y)
		slot.SetItemSlot(slotIndex, vnum, count)
		slot.RefreshSlot()
		self.tooltipItem = uiToolTip.ItemToolTip()
		slot.Show()

	def OverInItem(self,slotIndex):
		self.tooltipItem.ClearToolTip()
		self.tooltipItem.SetInventoryItem(slotIndex)
		self.tooltipItem.ShowToolTip()

	def OverOutItem(self):
		self.tooltipItem.HideToolTip()
		
class Component:

	def Button(self, parent, buttonName, tooltipText, x, y, func, UpVisual, OverVisual, DownVisual):
		button = ui.Button()
		if parent != None:
			button.SetParent(parent)
		button.SetPosition(x, y)
		button.SetUpVisual(UpVisual)
		button.SetOverVisual(OverVisual)
		button.SetDownVisual(DownVisual)
		button.SetText(buttonName)
		button.SetToolTipText(tooltipText)
		button.Show()
		button.SetEvent(func)
		return button

	
	def OnOffButton(self,parent,buttonName, tooltipText,x,y,image=None,OffUpVisual='OpenBot/Images/off_0.tga', OffOverVisual='OpenBot/Images/off_1.tga', OffDownVisual='OpenBot/Images/off_2.tga',OnUpVisual='OpenBot/Images/on_0.tga', OnOverVisual='OpenBot/Images/on_1.tga', OnDownVisual='OpenBot/Images/on_2.tga',xImgOffset = 15,yImgOffset = 15,funcState=None,defaultValue=0):
		if image != None:
			image = self.ExpandedImage(parent,x,y,image)
			x += xImgOffset
			y += yImgOffset

		button = OnOffButton(OffUpVisual, OffOverVisual, OffDownVisual,OnUpVisual, OnOverVisual, OnDownVisual,image=image,funcState=funcState,defaultValue=defaultValue)
		if parent != None:
			button.SetParent(parent)
		button.SetPosition(x, y)
		button.SetText("                "+ str(buttonName))
		button.SetToolTipText(tooltipText)
		#button.SetEvent(func)
		button.Show()
		return button	

		
	def HideButton(self, parent, buttonName, tooltipText, x, y, func, UpVisual, OverVisual, DownVisual):
		button = ui.Button()
		if parent != None:
			button.SetParent(parent)
		button.SetPosition(x, y)
		button.SetUpVisual(UpVisual)
		button.SetOverVisual(OverVisual)
		button.SetDownVisual(DownVisual)
		button.SetText(buttonName)
		button.SetToolTipText(tooltipText)
		button.SetEvent(func)
		return button

	def ToggleButton(self, parent, buttonName, tooltipText, x, y, funcUp, funcDown, UpVisual, OverVisual, DownVisual):
		button = ui.ToggleButton()
		if parent != None:
			button.SetParent(parent)
		button.SetPosition(x, y)
		button.SetUpVisual(UpVisual)
		button.SetOverVisual(OverVisual)
		button.SetDownVisual(DownVisual)
		button.SetText(buttonName)
		button.SetToolTipText(tooltipText)
		button.Show()
		button.SetToggleUpEvent(funcUp)
		button.SetToggleDownEvent(funcDown)
		return button

	def EditLine(self, parent, editlineText, x, y, width, heigh, max):
		SlotBar = ui.SlotBar()
		if parent != None:
			SlotBar.SetParent(parent)
		SlotBar.SetSize(width, heigh)
		SlotBar.SetPosition(x, y)
		SlotBar.Show()
		Value = ui.EditLine()
		Value.SetParent(SlotBar)
		Value.SetSize(width, heigh)
		Value.SetPosition(8, 2)
		Value.SetMax(max)
		Value.SetLimitWidth(width)
		Value.SetMultiLine()
		Value.SetText(editlineText)
		Value.SetIMEFlag(3)
		Value.Show()
		return SlotBar, Value
		
	def OnlyEditLine(self, parent, width, heigh, x, y, editlineText, max):
		Value = ui.EditLine()
		if parent != None:
			Value.SetParent(parent)
		Value.SetSize(width, heigh)
		Value.SetPosition(x, y)
		Value.SetMax(max)
		Value.SetText(editlineText)
		Value.SetNumberMode()
		Value.Show()
		return Value

	def TextLine(self, parent, textlineText, x, y, color):
		textline = ui.TextLine()
		if parent != None:
			textline.SetParent(parent)
		textline.SetPosition(x, y)
		if color != None:
			textline.SetFontColor(color[0], color[1], color[2])
		textline.SetText(textlineText)
		textline.SetOutline()
		textline.Show()
		return textline

	def RGB(self, r, g, b):
		return (r*255, g*255, b*255)

	def SliderBar(self, parent, sliderPos, func, x, y):
		Slider = ui.SliderBar()
		if parent != None:
			Slider.SetParent(parent)
		Slider.SetPosition(x, y)
		Slider.SetSliderPos(sliderPos)
		Slider.Show()
		Slider.SetEvent(func)
		return Slider

	def ExpandedImage(self, parent, x, y, img, tooltip=None):
		image = ui.ExpandedImageBox()
		if parent != None:
			image.SetParent(parent)
		image.SetPosition(x, y)
		image.LoadImage(img)
		image.Show()
		#image.SetToolTipText(tooltip)
		return image
		
	def ComboBoxFunc(self, parent, text, x, y, width, func):
		combo = ui.ComboBox()
		if parent != None:
			combo.SetParent(parent)
		combo.SetPosition(x, y)
		combo.SetSize(width, 15)
		combo.SetCurrentItem(text)
		combo.SetEvent(func)
		combo.Show()
		return combo
		
	def ComboBox(self, parent, text, x, y, width):
		combo = ui.ComboBox()
		if parent != None:
			combo.SetParent(parent)
		combo.SetPosition(x, y)
		combo.SetSize(width, 15)
		combo.SetCurrentItem(text)
		combo.Show()
		return combo

	def ThinBoard(self, parent, moveable, x, y, width, heigh, center):
		thin = ui.ThinBoard()
		if parent != None:
			thin.SetParent(parent)
		if moveable == TRUE:
			thin.AddFlag('movable')
			thin.AddFlag('float')
		thin.SetSize(width, heigh)
		thin.SetPosition(x, y)
		if center == TRUE:
			thin.SetCenterPosition()
		thin.Show()
		return thin

	def Gauge(self, parent, width, color, x, y):
		gauge = ui.Gauge()
		if parent != None:
			gauge.SetParent(parent)
		gauge.SetPosition(x, y)
		gauge.MakeGauge(width, color)
		gauge.Show()
		return gauge
		
	def ListBoxEx(self, parent, x, y, width, heigh):
		bar = ui.Bar()
		if parent != None:
			bar.SetParent(parent)
		bar.SetPosition(x, y)
		bar.SetSize(width + 20, heigh)
		bar.SetColor(1996488704)
		bar.Show()
		ListBox = ui.ListBoxEx()
		ListBox.SetParent(bar)
		ListBox.SetPosition(0, 0)
		ListBox.SetViewItemCount(11)
		ListBox.SetSize(width, heigh)
		ListBox.Show()
		scroll = ui.ScrollBar()
		scroll.SetParent(bar)
		scroll.SetPosition(width + 5, 0)
		scroll.SetScrollBarSize(heigh)
		scroll.Show()
		ListBox.SetScrollBar(scroll)
		return (bar, ListBox, scroll)

	def ListBoxEx2(self, parent, x, y, width, heigh):
		bar = ui.Bar()
		if parent != None:
			bar.SetParent(parent)
		bar.SetPosition(x, y)
		bar.SetSize(width + 20, heigh)
		bar.SetColor(1996488704)
		bar.Show()
		ListBox = ui.ListBoxEx()
		ListBox.SetParent(bar)
		ListBox.SetPosition(0, 0)
		ListBox.SetViewItemCount(5)
		ListBox.SetSize(width, heigh)
		ListBox.Show()
		scroll = ui.ScrollBar()
		scroll.SetParent(bar)
		scroll.SetPosition(width + 5, 0)
		scroll.SetScrollBarSize(heigh)
		scroll.Show()
		ListBox.SetScrollBar(scroll)
		return (bar, ListBox, scroll)	
		
	def FileListBox(self, parent, x, y, width, heigh, count):
		ListBox = ui.ListBoxEx()
		ListBox.SetParent(parent)
		ListBox.SetPosition(x, y)
		ListBox.SetViewItemCount(count)
		ListBox.SetSize(width, heigh)
		ListBox.Show()
		scroll = ui.ScrollBar()
		scroll.SetParent(ListBox)
		scroll.SetPosition(width - 20, 0)
		scroll.SetScrollBarSize(heigh)
		scroll.Show()
		ListBox.SetScrollBar(scroll)
		return ListBox, scroll
		
	def ReadingListBox(self, parent, x, y, width, heigh, count):
		bar = ui.Bar()
		if parent != None:
			bar.SetParent(parent)
		bar.SetPosition(x, y)
		bar.SetSize(width + 20, heigh)
		bar.Show()
		ListBox = ui.ListBoxEx()
		ListBox.SetParent(bar)
		ListBox.SetPosition(10, 13)
		ListBox.SetViewItemCount(count)
		ListBox.SetSize(width, heigh)
		ListBox.Show()
		return bar, ListBox


class TabWindow(ui.Window):
	def __init__(self,x,y,size_x,size_y,parent,list_tab_names):
		ui.Window.__init__(self)
		self.SetParent(parent)
		self.SetPosition(x,y)
		self.SetSize(size_x,size_y)
		self.Show()

		self.header = ui.ThinBoard()
		self.header.SetParent(self)
		self.header.SetSize(size_x, 35)
		self.header.SetPosition(0,0)
		self.header.Show()


		#Buttons and tabs
		self.curTab = 0
		self.tabs = [] #Array of tuples, the tupple is represented as (button,tab)
		for i,name in enumerate(list_tab_names):
			
			tabWindow = ui.ThinBoard()
			tabWindow.SetParent(self)
			tabWindow.SetSize(size_x, size_y-35)
			tabWindow.SetPosition(0, 35)
			tabWindow.Hide()

			radioButton = ui.RadioButton()
			radioButton.SetParent(self.header)
			radioButton.SetUpVisual("d:/ymir work/ui/public/small_button_01.sub")
			radioButton.SetOverVisual("d:/ymir work/ui/public/small_button_02.sub")
			radioButton.SetDownVisual("d:/ymir work/ui/public/small_button_03.sub")
			radioButton.SetText(name)
			radioButton.SetPosition(10+52*i, 0)
			radioButton.SetWindowVerticalAlignCenter()
			radioButton.Show()
			self.tabs.append((radioButton,tabWindow))
		
		self.tabButtonGroup = ui.RadioButtonGroup.Create([ [btn[0],self._OnClickTabButton,None] for i,btn in enumerate(self.tabs)])



	def __del__(self):
		ui.Window.__del__(self)

	def GetTab(self,num):
		return self.tabs[num][1]
		
	def _OnClickTabButton(self, id):
		self.SetCurTab(id)

	def GetCurTab(self):
		return self.tabs[self.curTab][1]

	def SetCurTab(self, tab):
		self.curTab = tab
		self.RefreshTab()
		
	def RefreshTab(self):
		for btn,page in self.tabs:
			page.Hide()
		self.GetCurTab().Show()


#Return a button,slider and label, all *args and **kwargs are used on button
def GetSliderButtonLabel(parent,callback,*args,**kwargs):
	comp = Component()
	if "offsetX" in kwargs:
		offsetX = kwargs.pop('offsetX')
	else:
		offsetX = 0

	if "offsetY" in kwargs:
		offsetY = kwargs.pop('offsetY')
	else:
		offsetY = 0

	if "defaultSlider" in kwargs:
		defaultSlider = kwargs.pop('defaultSlider')
	else:
		defaultSlider = 0

	redPotButton = comp.OnOffButton(parent,*args,**kwargs)
	SlideRedPot = comp.SliderBar(parent, defaultSlider, callback,redPotButton.GetLocalPosition()[0]+offsetX+20,redPotButton.GetLocalPosition()[1]+offsetY) # 45, 31)
	redPotLabel = comp.TextLine(parent, "1", SlideRedPot.GetLocalPosition()[0] + 185, SlideRedPot.GetLocalPosition()[1], comp.RGB(255, 255, 255))
	return (redPotButton,SlideRedPot,redPotLabel)