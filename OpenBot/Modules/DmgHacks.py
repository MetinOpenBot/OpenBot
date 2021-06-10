import eXLib,ui,net,chr,player,chat,item
import OpenLib,FileManager,Movement,UIComponents
from FileManager import boolean
ATTACK_MAX_DIST_NO_TELEPORT = 290


class DmgHacks(ui.Window):
	def __init__(self):
		ui.Window.__init__(self)
		self.pause = False
		self.BuildWindow()

	def __del__(self):
		ui.Window.__del__(self)

	def BuildWindow(self):
		self.Board = ui.BoardWithTitleBar()
		self.Board.SetSize(300, 260)
		self.Board.SetCenterPosition()
		self.Board.AddFlag('movable')
		self.Board.AddFlag('float')
		self.Board.SetTitleName('WaitHack')
		self.Board.SetCloseEvent(self.Close)
		self.Board.Hide()
		self.comp = UIComponents.Component()

		self.enableButton = self.comp.OnOffButton(self.Board, '', '', 130, 200, OffUpVisual='OpenBot/Images/start_0.tga', OffOverVisual='OpenBot/Images/start_1.tga', OffDownVisual='OpenBot/Images/start_2.tga',OnUpVisual='OpenBot/Images/stop_0.tga', OnOverVisual='OpenBot/Images/stop_1.tga', OnDownVisual='OpenBot/Images/stop_2.tga' )
  		self.playerClose = self.comp.OnOffButton(self.Board, '', '', 130, 50)
		self.RangeLabel = self.comp.TextLine(self.Board, 'Range', 13, 92, self.comp.RGB(255, 255, 255))
		self.SpeedLabel = self.comp.TextLine(self.Board, 'Speed', 13, 126, self.comp.RGB(255, 255, 255))
		self.MonsterLabel = self.comp.TextLine(self.Board, 'Monsters', 13, 160, self.comp.RGB(255, 255, 255))
		self.PlayerLabel = self.comp.TextLine(self.Board, 'Stop when player close', 12, 51, self.comp.RGB(255, 255, 255))
  		self.rangeNum = self.comp.TextLine(self.Board, '100', 254, 92, self.comp.RGB(255, 255, 255))
		self.speedNum = self.comp.TextLine(self.Board, '100 ms', 254, 125, self.comp.RGB(255, 255, 255))
		self.monsterNum = self.comp.TextLine(self.Board, '100', 254, 160, self.comp.RGB(255, 255, 255))
		self.RangeSlider = self.comp.SliderBar(self.Board, 0.0, self.Range_func, 73, 94)
		self.SpeedSlider = self.comp.SliderBar(self.Board, 0.0, self.Speed_func, 73, 127)
		self.MonsterSlider = self.comp.SliderBar(self.Board, 0.0, self.Monster_func, 73, 161)
		self.enableButton.SetOff()

		self.loadSettings()

		self.range = 0
		self.speed = 0
		self.lastTime = 0
		self.maxMonster = 0
		self.Speed_func()
		self.Range_func()
		self.Monster_func()

	def loadSettings(self):
		self.MonsterSlider.SetSliderPos(float(FileManager.ReadConfig("WaitHack_MaxMonsters")))
		self.SpeedSlider.SetSliderPos(float(FileManager.ReadConfig("WaitHack_Speed")))
		self.RangeSlider.SetSliderPos(float(FileManager.ReadConfig("WaitHack_Range")))
		self.playerClose.SetValue(boolean(FileManager.ReadConfig("WaitHack_PlayerClose")))
	def saveSettings(self):
		FileManager.WriteConfig("WaitHack_MaxMonsters", str(self.MonsterSlider.GetSliderPos()))
		FileManager.WriteConfig("WaitHack_Speed", str(self.SpeedSlider.GetSliderPos()))
		FileManager.WriteConfig("WaitHack_Range", str(self.RangeSlider.GetSliderPos()))
		FileManager.WriteConfig("WaitHack_PlayerClose", str(self.playerClose.isOn))
		FileManager.Save()
	
	
	def Monster_func(self):
		self.maxMonster = int(self.MonsterSlider.GetSliderPos()*1000)
		self.monsterNum.SetText(str(self.maxMonster))
  
	def Range_func(self):
		self.range = int(self.RangeSlider.GetSliderPos()*10000)
		self.rangeNum.SetText(str(self.range))
	
	def Speed_func(self):
		self.speed= float(self.SpeedSlider.GetSliderPos())
		self.speedNum.SetText(str(int(self.speed*1000)) + ' ms')
	
	
	def OpenWindow(self):
		if self.Board.IsShow():
			self.Board.Hide()
		else:
			self.Board.Show()
   
	def TeleportAttack(self,lst,x,y):
		Movement.TeleportStraightLine(self.lastPos[0],self.lastPos[1],x,y)
		self.lastPos = (x,y)
		#eXLib.SendStatePacket(x,y,0,eXLib.CHAR_STATE_STOP,0)
		vid_hits = 0
		for vid in lst:
			mob_x, mob_y, mob_z = chr.GetPixelPosition(vid)
			if OpenLib.dist(x,y,mob_x,mob_y) < ATTACK_MAX_DIST_NO_TELEPORT:
				#chat.AppendChat(3,"Sent Attack, X:" + str(mob_x) + " Y:" + str(mob_y) + "VID: " +str(vid))
				eXLib.SendAttackPacket(vid,0)
				lst.remove(vid)
				vid_hits+=1
		
		return vid_hits
		#chat.AppendChat(3,"After: " + str(len(lst)))

	def IsWeaponArch(self):
		idx = player.GetItemIndex(player.EQUIPMENT,item.EQUIPMENT_WEAPON)
		if idx == 0:
			return False
		item.SelectItem(idx)
		if item.GetItemType() == item.ITEM_TYPE_WEAPON and item.GetItemSubType() == item.WEAPON_BOW:
			return True
		return False

	def AttackArch(self,lst,x,y):
		vid_hits = 0
		#chat.AppendChat(3,"Attacking with arch")
		for enemy in lst:
			x,y,z = chr.GetPixelPosition(enemy)
			eXLib.SendAddFlyTarget(enemy,x,y)
			eXLib.SendShoot(eXLib.COMBO_SKILL_ARCH)
			lst.remove(enemy)
			vid_hits+=1
		return vid_hits
    
				
	def OnUpdate(self):
		val, self.lastTime = OpenLib.timeSleep(self.lastTime,self.speed)
		if(val and self.enableButton.isOn and not self.pause):
			if OpenLib.GetCurrentPhase() != OpenLib.PHASE_GAME:
				return
			isArch = self.IsWeaponArch()
			main_vid = net.GetMainActorVID()
			x,y,z = chr.GetPixelPosition(main_vid)
			self.lastPos = (x,y)
			lst = list()

   			for vid in eXLib.InstancesList:
				if vid == main_vid:
					continue

				if not chr.HasInstance(vid):
					continue
				if self.playerClose.isOn and chr.GetInstanceType(vid) == OpenLib.PLAYER_TYPE and vid != net.GetMainActorVID():
					return
				if player.GetCharacterDistance(vid) < self.range and not eXLib.IsDead(vid):	
					lst.append(vid)
			hit_counter = 0
			i = 0
			while len(lst) > 0 and hit_counter < self.maxMonster:
				vid = lst[0]
				mob_x, mob_y, mob_z = chr.GetPixelPosition(vid)
				if eXLib.IsPositionBlocked(mob_x,mob_y):
					lst.remove(vid)
					continue
				#Checking the distance between teleports might increase the range and make it more stable
				if isArch:
					hit_counter+=self.AttackArch(lst,mob_x, mob_y)
				else:
					hit_counter+=self.TeleportAttack(lst,mob_x, mob_y)
				i+=1
			Movement.TeleportStraightLine(self.lastPos[0],self.lastPos[1],x,y)
	def Close(self):
		self.Board.Hide()
		self.saveSettings()

def Pause():
	"""
	Pauses the damage hack.
	"""
	Dmg.pause = True

def Resume():
	"""
	Resumes damage hack.
	"""
	Dmg.pause = False

def switch_state():
	"""
	Open's or closes the UI window.
	"""
	Dmg.OpenWindow()

Dmg = DmgHacks()
Dmg.Show()