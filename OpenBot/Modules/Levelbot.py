import Movement
import OpenLib,chr,player,eXLib,ui,chat,background
import FileManager,UIComponents
from BotBase import BotBase
from FileManager import boolean



class LevelBotDialog(BotBase):

	STATE_WAIT = 0
	STATE_LEVELING = 1

	TIME_WAIT = 0.5

	class LocationCondition:
		def __init__(self,level,locationX,locationY,map):
			self.level = level
			self.locationX = locationX
			self.locationY = locationY
			self.map = map

		def parseLocation(self,string):
			all = string.split("|")
			self.level = int(all[0].split(":")[1])
			self.locationX = int(all[1].split(":")[1])*100
			self.locationY = int(all[2].split(":")[1])*100
			self.map = all[3].split(":")[1]

		
		def __hash__(self):
			return self.level

		def __eq__(self, o):
			if isinstance(o,self.__class__):
				return self.level == o.level
			return self.level == o
		
		def __str__(self):
			return "Level:" +str(self.level) + "|X:"+str(int(self.locationX/100))+"|Y:"+str(int(self.locationY/100))+"|Map:"+str(self.map)


	def __init__(self):
		BotBase.__init__(self,self.TIME_WAIT,waitIsPlayerDead=True)
		self.Range = 20000
		self.startPosition = (0,0)
		self.goToCenter = False
		self.ignoreBlockedPosition = True

		#Location Changer
		self.allowLocChanger = False
		self.locations = set()


		self.levelState = self.STATE_LEVELING
		self.LoadSettings()
		self.BuildWindow()


	def BuildWindow(self):
		self.Board = ui.BoardWithTitleBar() 
		self.Board.SetPosition(52, 40)
		self.Board.SetSize(300, 380) 
		self.Board.SetTitleName("LevelBot")
		self.Board.AddFlag("movable")
		self.Board.SetCloseEvent(self.Close)
		self.Board.Hide()

		comp = UIComponents.Component()
		self.rangeLabel = comp.TextLine(self.Board, "Range", 25, 40, comp.RGB(255, 255, 255))
		self.slideRange = comp.SliderBar(self.Board, float(self.Range/20000.0), self.OnSlideRange,self.rangeLabel.GetLocalPosition()[0]+40,self.rangeLabel.GetLocalPosition()[1]+5)
		self.rangeNumLabel = comp.TextLine(self.Board, self.Range,self.slideRange.GetLocalPosition()[0] + 185, self.slideRange.GetLocalPosition()[1], comp.RGB(255, 255, 255))
		self.ignoreInWallsBtn = comp.OnOffButton(self.Board, '\t\t\t\t\t\t\tIgnore Mobs in Walls', "Don't attack mobs in walls", 20, 80,funcState=self.OnIgnoreInWall,defaultValue=int(self.ignoreBlockedPosition))
		self.goToCenterBtn = comp.OnOffButton(self.Board, '\t\t\tGo to center', "Go to center when no moobs near", 170, 80,funcState=self.OnGoToCenter,defaultValue=int(self.goToCenter))
		self.goToShopBtn = comp.OnOffButton(self.Board, '\t\tGo to shop', "Go to shop when inventory full", 20, 115,funcState=self.SetShopOnInvFull,defaultValue=int(self.allowShopOnFullInv))
		
		self.EnableButton = comp.OnOffButton(self.Board, '', '', 0,323,OffUpVisual='OpenBot/Images/start_0.tga', OffOverVisual='OpenBot/Images/start_1.tga', OffDownVisual='OpenBot/Images/start_2.tga',OnUpVisual='OpenBot/Images/stop_0.tga', OnOverVisual='OpenBot/Images/stop_1.tga', OnDownVisual='OpenBot/Images/stop_2.tga',funcState=self.OnStartStop)
		self.EnableButton.SetWindowHorizontalAlignCenter()

		#Location stuff
		self.labelChanger = comp.TextLine(self.Board, 'Location Changer', 110, 140, comp.RGB(255, 255, 0))
		self.locationActivateBtn = comp.OnOffButton(self.Board, '\t\t\t\t\tChange location', "Change locations based on level", 20, 160,funcState=self.OnLocationBtnChange,defaultValue=int(self.allowLocChanger))
		self.removeLocButton = comp.Button(self.Board, 'Remove', 'Remove selected entry', 212, 160,  self.OnRemoveSelected, 'd:/ymir work/ui/public/Middle_Button_01.sub', 'd:/ymir work/ui/public/Middle_Button_02.sub', 'd:/ymir work/ui/public/Middle_Button_03.sub')
		self.barItems, self.fileListBox, self.ScrollBar = comp.ListBoxEx2(self.Board, 20, 187, 235, 100)
		self.levelSlotBar, self.levelEditLine = comp.EditLine(self.Board, '', 182, 295, 30, 15, 3)
		self.locationText = comp.TextLine(self.Board, 'Current location starting on level ', 27, 295, comp.RGB(255, 255, 255))
		self.addLocButton = comp.Button(self.Board, 'Add', '', 222, 293,  self.OnAddLocation, 'd:/ymir work/ui/public/small_Button_01.sub', 'd:/ymir work/ui/public/small_Button_02.sub', 'd:/ymir work/ui/public/small_Button_03.sub')
		
		#Init
		self.OnSlideRange()
		self.UpdateLocationList()

	def LoadSettings(self):
		self.Range = int(FileManager.ReadConfig("LevelRange"))
		self.goToCenter = boolean(FileManager.ReadConfig("LevelGoToCenter"))
		self.ignoreBlockedPosition = boolean(FileManager.ReadConfig("LevelIgnoreBlockedPos"))
		self.allowShopOnFullInv = boolean(FileManager.ReadConfig("LevelShopFullInv"))
		self.allowLocChanger = boolean(FileManager.ReadConfig("LevelAllowLocation"))
		locs = FileManager.LoadListFile(FileManager.CONFIG_LOCATION_CHANGER)
		for loc in locs:
			this_loc = self.LocationCondition(0,0,0,0)
			try:
				this_loc.parseLocation(loc)
				self.locations.add(this_loc)
			except Exception:
				continue

	def SaveSettings(self):
		#chat.AppendChat(3,str(self.Range))
		FileManager.WriteConfig("LevelRange", str(self.Range))
		FileManager.WriteConfig("LevelGoToCenter", str(self.goToCenter))
		FileManager.WriteConfig("LevelIgnoreBlockedPos", str(self.ignoreBlockedPosition))
		FileManager.WriteConfig("LevelShopFullInv", str(self.allowShopOnFullInv))
		FileManager.WriteConfig("LevelAllowLocation", str(self.allowLocChanger))
		FileManager.SaveListFile(FileManager.CONFIG_LOCATION_CHANGER,self.locations)
		FileManager.Save()


	#UI
	def OnRemoveSelected(self):
		_item = self.fileListBox.GetSelectedItem()
		if _item == None:
			return
		lvl = int(_item.GetText().split("|")[0].split(":")[1])
		self.locations.remove(lvl)
		self.UpdateLocationList()

	def OnLocationBtnChange(self,val):
		self.allowLocChanger = val

	def OnAddLocation(self):
		level = int(self.levelEditLine.GetText())
		position = player.GetMainCharacterPosition()
		curr_map = background.GetCurrentMapName()
		loc = self.LocationCondition(level,position[0],position[1],curr_map)
		self.locations.add(loc)
		self.UpdateLocationList()

	def UpdateLocationList(self):
		self.fileListBox.RemoveAllItems()
		for loc in sorted(self.locations,key=lambda x:x.level):
			self.fileListBox.AppendItem(OpenLib.Item(str(loc)))

	def OnIgnoreInWall(self,val):
		self.ignoreBlockedPosition = val

	def OnGoToCenter(self,val):
		self.goToCenter = val

	def OnSlideRange(self):
		self.Range = int(self.slideRange.GetSliderPos()*20000)
		self.rangeNumLabel.SetText(str(self.Range))

	def OnStartStop(self,val):
		if val:
			self.Start()
		else:
			self.Stop()


	
	#Logic
	def Close(self):
		self.SaveSettings()
		self.Board.Hide()

	def SetStateLeveling(self):
		self.levelState = self.STATE_LEVELING
	
	def SetStateWait(self):
		self.levelState = self.STATE_WAIT

	def GetNextMonster(self):
		(closest_vid,_dist) = (0,999999999)
		my_pos = player.GetMainCharacterPosition()
		for vid in eXLib.InstancesList:
			if not chr.HasInstance(vid):
				continue

			if eXLib.IsDead(vid):
				continue

			_type = chr.GetInstanceType(vid)
			monst_pos = chr.GetPixelPosition(vid)

			if self.ignoreBlockedPosition and eXLib.IsPositionBlocked(monst_pos[0],monst_pos[1]):
				continue

			if _type != OpenLib.MONSTER_TYPE:
				continue

			if OpenLib.dist(self.startPosition[0],self.startPosition[1],monst_pos[0],monst_pos[1]) > self.Range:
				continue
			
			this_dist = OpenLib.dist(my_pos[0],my_pos[1],monst_pos[0],monst_pos[1])

			if this_dist < _dist:
				_dist = this_dist
				closest_vid = vid
		
		return closest_vid

	def _PositionArriveCallback(self):
		self.SetStateLeveling()

	
	def CheckChangeLocation(self):
		currLevel = player.GetStatus(player.LEVEL)
		resultLoc = 0
		for loc in self.locations:
			if loc.level > currLevel:
				continue
			if resultLoc == 0:
				resultLoc = loc
				continue
			if  loc.level > resultLoc.level:
				resultLoc = loc
		if resultLoc != 0 and ( int(resultLoc.locationX) != int(self.startPosition[0]) or int(resultLoc.locationY) != int(self.startPosition[1]) or background.GetCurrentMapName() != resultLoc.map):
			chat.AppendChat(3,"Going to " + str(resultLoc.map) + " X:" + str(resultLoc.locationX) + " Y:" + str(resultLoc.locationY))
			self.SetStateWait()
			Movement.GoToPositionAvoidingObjects(resultLoc.locationX,resultLoc.locationY,callback=self._PositionArriveCallback,mapName=resultLoc.map)
			self.startPosition = (resultLoc.locationX,resultLoc.locationY)
			return True
		return False

	
	#Abstract Functions
	def CanPause(self):
		if self.levelState == self.STATE_WAIT:
			return False
		return True

	def Resume(self):
		self.SetStateLeveling()
		pass

	def Pause(self):
		player.SetAttackKeyState(False)
		pass

	def StartBot(self):
		self.startPosition = player.GetMainCharacterPosition()
		self.Resume()

	def StopBot(self):
		self.Pause()

	def Frame(self):
		if self.levelState == self.STATE_LEVELING:
			if self.allowLocChanger and self.CheckChangeLocation():
				return
			monster = self.GetNextMonster()
			if monster != 0:
				OpenLib.AttackTarget(monster)
			elif self.goToCenter:
				Movement.GoToPositionAvoidingObjects(self.startPosition[0],self.startPosition[1])
		
		elif self.levelState == self.STATE_WAIT:
			return

def switch_state():
	if not level.Board.IsShow():
		level.Board.Show()
	else:
		level.Close()

level = LevelBotDialog()
level.Show()