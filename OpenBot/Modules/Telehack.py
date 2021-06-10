import ui,app,net,player,chr,miniMap,wndMgr,background,math,uiMiniMap,OpenLib,chat,exception,Movement

TeleportHackMode = "Teleport"
timerrBlock = 0	

class TeleportHackDialog(ui.ScriptWindow):

	CurrentMapName = ""
	
	class AtlasRenderer(ui.Window):
		def __init__(self):
			ui.Window.__init__(self)
			self.AddFlag("not_pick")
		#	self.AddFlag('movable')

		def OnUpdate(self):
			miniMap.UpdateAtlas()

		def OnRender(self):
			(PosX, PosY) = self.GetGlobalPosition()
			miniMap.RenderAtlas(float(PosX), float(PosY))
			
				
			if app.IsPressed(app.DIK_LSHIFT):
				(mouseX, mouseY) = wndMgr.GetMousePosition()
				(bFind, sName, iPosX, iPosY, dwTextColor, dwGuildID) = miniMap.GetAtlasInfo(mouseX, mouseY)
				
				(iSizeX, iSizeY, SizeX, SizeY) = GetCurrentMapSize()
				
				if not bFind:
					width = 6
					MapSizeX = miniMap.GetAtlasSize()[1]
					if MapSizeX == 0:
						size = 6
					else:
						size = DivideToFloat(SizeX * 256, miniMap.GetAtlasSize()[1])
					(sName, iPosX, iPosY, dwTextColor) = "", (mouseX - PosX) * size + width, (mouseY - PosY) * size, -8722595
				
				if iPosX < 0 or iPosY < 0 or iPosX > SizeX * 256 or iPosY > SizeY * 256:
					return
				 
				self.TeleportToDest(iPosX*100, iPosY*100)

		def TeleportToDest(self, aimx, aimy):
			global TeleportHackMode,timerrBlock
			val, timerrBlock = OpenLib.timeSleep(timerrBlock,2) #Avoid multiple calls on same keypress
			if val == False:
				return
			if TeleportHackMode == "Walk":
				chat.AppendChat(3,str(aimx) + " " + str(aimy))
				Movement.GoToPositionAvoidingObjects(aimx,aimy)
			else:
				Movement.TeleportToPosition(aimx,aimy)
		def Debug(self):
			pass
			#player.SetSingleDIKKeyState(app.DIK_UP, TRUE)
			#player.SetSingleDIKKeyState(app.DIK_UP, FALSE)			

		def ShowAtlas(self):
			miniMap.ShowAtlas()

		def HideAtlas(self):
			miniMap.HideAtlas()

	def __init__(self):
		self.tooltipInfo = uiMiniMap.MapTextToolTip()
		self.tooltipInfo.Hide()
		self.AtlasMainWindow = None
		self.board = 0
		self.CurrentMapName = background.GetCurrentMapName()
		ui.ScriptWindow.__init__(self)
		self.LoadWindow()	

	def LoadWindow(self):
		try:
			pyScrLoader = ui.PythonScriptLoader()
			pyScrLoader.LoadScriptFile(self, "UIScript/AtlasWindow.py")
		except:
			exception.Abort("AtlasWindow.LoadWindow.LoadScript")

		try:
			self.board = self.GetChild("board")
			self.board.SetTitleName("Teleporthack")

		except:
			exception.Abort("AtlasWindow.LoadWindow.BindObject")

		self.AtlasMainWindow = self.AtlasRenderer()
		self.board.SetCloseEvent(self.Hide)
		self.AtlasMainWindow.SetParent(self.board)
		self.AtlasMainWindow.SetPosition(7, 30)
		self.tooltipInfo.SetParent(self.board)
		self.SetPosition(52, 40)
		
		self.Line = ui.Line()
		self.Line.SetParent(self)
		self.Line.SetColor(0xff777777)
		self.Line.Show()
		
		self.ModeText = ui.TextLine()
		self.ModeText.SetParent(self)
		self.ModeText.SetText("Mode:")
		self.ModeText.Show()

		self.PositionText = ui.TextLine()
		self.PositionText.SetParent(self)
		self.PositionText.SetFontColor(1.0, 0.8, 0)	#SetFontColor(0.2, 0.2, 1.0)
		self.PositionText.SetText("(200, 800)")
		self.PositionText.Show()
		
		global TeleportHackMode
		self.ModeButton = ui.Button()
		self.ModeButton.SetParent(self)
		self.ModeButton.SetUpVisual("d:/ymir work/ui/public/middle_button_01.sub")
		self.ModeButton.SetOverVisual("d:/ymir work/ui/public/middle_button_02.sub")
		self.ModeButton.SetDownVisual("d:/ymir work/ui/public/middle_button_03.sub")
		self.ModeButton.SetText(TeleportHackMode)		
		self.ModeButton.SetEvent(lambda : self.ChangeMode())
		self.ModeButton.Show()
		
		self.Hide()
		
	def switch_state(self):
		if self.IsShow():
			self.Hide()
		else:
			chat.AppendChat(3,"[Teleport] To move/teleport to a location press shift with the mouse over the location.")
			self.Show()

	def ChangeMode(self):
		global TeleportHackMode
		if TeleportHackMode == "Teleport":
			TeleportHackMode = "Walk"
		else:
			TeleportHackMode = "Teleport"
		self.ModeButton.SetText(TeleportHackMode)
		
	def Hide(self):
		ui.ScriptWindow.Hide(self)

	def Show(self):			
		if self.AtlasMainWindow:
			(iSizeX, iSizeY, SizeX, SizeY) = GetCurrentMapSize()
			self.SetSize(iSizeX + 15, iSizeY + 38 + 30)
			self.board.SetSize(iSizeX + 15, iSizeY + 38 + 30)
			self.Line.SetPosition(7, iSizeY + 31)
			self.Line.SetSize(iSizeX, 0)
			self.ModeText.SetPosition(15, iSizeY + 38)
			self.ModeButton.SetPosition(55, iSizeY + 36)
			self.PositionText.SetPosition(125, iSizeY + 38)
			
			self.AtlasMainWindow.ShowAtlas()
			self.AtlasMainWindow.Show()
		ui.ScriptWindow.Show(self)

	def OnUpdate(self):
		(PlayerX, PlayerY, PlayerZ) = player.GetMainCharacterPosition()
		self.PositionText.SetText("(%s, %s)" % (int(PlayerX / 100), int(PlayerY / 100)))
	
		if background.GetCurrentMapName() != self.CurrentMapName:
			self.Show()
			self.CurrentMapName = background.GetCurrentMapName()
	
		miniMap.ShowAtlas()
		if not self.tooltipInfo:
			return

		self.tooltipInfo.Hide()

		if FALSE == self.board.IsIn():
			return

		(mouseX, mouseY) = wndMgr.GetMousePosition()
		(bFind, sName, iPosX, iPosY, dwTextColor, dwGuildID) = miniMap.GetAtlasInfo(mouseX, mouseY)

		(PosX, PosY) = self.GetGlobalPosition()
		
		(iSizeX, iSizeY, SizeX, SizeY) = GetCurrentMapSize()
		if not bFind:
			MapSizeX = miniMap.GetAtlasSize()[1]
			if MapSizeX == 0:
				size = 6
			else:
				size = DivideToFloat(SizeX * 256, miniMap.GetAtlasSize()[1])
			height = 30 * size
			width = 6 * size
			(sName, iPosX, iPosY, dwTextColor) = "", (mouseX - PosX) * size - width, (mouseY - PosY) * size - height, -8722595
			
		if iPosX < 0 or iPosY < 0 or iPosX > SizeX * 256 or iPosY > SizeY * 256:
			return

		self.tooltipInfo.SetText("%s(%d, %d)" % (sName, iPosX, iPosY))
		(x, y) = self.GetGlobalPosition()
		self.tooltipInfo.SetTooltipPosition(mouseX - x, mouseY - y)
		self.tooltipInfo.SetTextColor(dwTextColor)
		self.tooltipInfo.Show()
		self.tooltipInfo.SetTop()

	def OnPressEscapeKey(self):
		self.Hide()
		return TRUE
		
MapBuffer = {}		
def GetCurrentMapSize():
	global MapBuffer
	ActualMapName = background.GetCurrentMapName()
	if ActualMapName in MapBuffer:
		return MapBuffer[ActualMapName]
	else:
		(bGet, iSizeX, iSizeY) = miniMap.GetAtlasSize()
		GetMapData = str(OpenLib.EterPackOperator("atlasinfo.txt").read())
		MapData = GetMapData.split("\n")
		for Map in MapData:
			try:
				MapName = Map.split("\t")[0]
				SizeX = int(Map.split("\t")[3])
				SizeY = int(Map.split("\t")[4])
				if MapName == ActualMapName:
					if iSizeX == 0 or iSizeY == 0:
						iSizeX = SizeX * 43
						iSizeY = SizeY * 43
					break
			except:
				pass
		MapBuffer[ActualMapName] = (iSizeX, iSizeY, SizeX, SizeY)
		return(iSizeX, iSizeY, SizeX, SizeY)
		
def GetTmpTeleport(DestX, DestY):
	(PlayerX, PlayerY, PlayerZ) = player.GetMainCharacterPosition()
	DifX = DestX - PlayerX
	DifY = DestY - PlayerY
	Vektor = DivideToFloat(2000, math.sqrt(DifX**2 + DifY**2))
	TempX = PlayerX + Vektor*DifX
	TempY = PlayerY + Vektor*DifY
	Count = DivideToFloat((DestX - PlayerX), (Vektor*DifX))
	return (TempX, TempY, Count)
		
def DivideToFloat(x, y):
	try:
		return x * (y**-1)
	except:
		return 0		
		

