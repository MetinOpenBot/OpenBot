import eXLib,ui,net,chr,player,chat,item,skill
import OpenLib,FileManager,Movement,UIComponents
from FileManager import boolean


CLOUD_SKILL_STATE_WAITING = 0
CLOUD_SKILL_STATE_READY = 1
CLOUD_SKILL_STATE_USED = 2


class DmgHacksInstance(ui.Window):
	def __init__(self):
		ui.Window.__init__(self)
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

		self.enableButton = self.comp.OnOffButton(self.Board, '', '', 130, 210, OffUpVisual='OpenBot/Images/start_0.tga', OffOverVisual='OpenBot/Images/start_1.tga', OffDownVisual='OpenBot/Images/start_2.tga',OnUpVisual='OpenBot/Images/stop_0.tga', OnOverVisual='OpenBot/Images/stop_1.tga', OnDownVisual='OpenBot/Images/stop_2.tga',funcState=self.OnOffBtnState )
  		self.playerClose = self.comp.OnOffButton(self.Board, '', '', 130, 50)
		self.wallBtn = self.comp.OnOffButton(self.Board, '\t\t\t\tCheck is wall', 'Dont attack mobs with wall in between', 170, 30)
		self.cloudBtn = self.comp.OnOffButton(self.Board, '\t\t\t\tCloud exploit', 'Only on dagger ninja', 170, 50)
		self.attackPlayerBtn = self.comp.OnOffButton(self.Board, '\t\t\t\tAttack players', '', 170, 70)
		self.attackBlockedMonsters = self.comp.OnOffButton(self.Board, '\t\t\t\t', '', 130, 70)
		self.AttackBlockedMonsers = self.comp.TextLine(self.Board, 'Attack blocked monsters', 13, 70, self.comp.RGB(255, 255, 255))
		self.RangeLabel = self.comp.TextLine(self.Board, 'Range', 13, 102, self.comp.RGB(255, 255, 255))
		self.SpeedLabel = self.comp.TextLine(self.Board, 'Speed', 13, 136, self.comp.RGB(255, 255, 255))
		self.MonsterLabel = self.comp.TextLine(self.Board, 'Monsters', 13, 170, self.comp.RGB(255, 255, 255))
		self.PlayerLabel = self.comp.TextLine(self.Board, 'Stop when player close', 12, 51, self.comp.RGB(255, 255, 255))
  		self.rangeNum = self.comp.TextLine(self.Board, '100', 254, 102, self.comp.RGB(255, 255, 255))
		self.speedNum = self.comp.TextLine(self.Board, '100 ms', 254, 136, self.comp.RGB(255, 255, 255))
		self.monsterNum = self.comp.TextLine(self.Board, '100', 254, 170, self.comp.RGB(255, 255, 255))
		self.RangeSlider = self.comp.SliderBar(self.Board, 0.0, self.Range_func, 73, 104)
		self.SpeedSlider = self.comp.SliderBar(self.Board, 0.0, self.Speed_func, 73, 137)
		self.MonsterSlider = self.comp.SliderBar(self.Board, 0.0, self.Monster_func, 73, 171)
		self.enableButton.SetOff()

		self.loadSettings()

		self.range = 0
		self.speed = 0
		self.lastTime = 0
		self.maxMonster = 0
		self.cloudSkillState = CLOUD_SKILL_STATE_READY
		self.Speed_func()
		self.Range_func()
		self.Monster_func()

	def loadSettings(self):
		self.MonsterSlider.SetSliderPos(float(FileManager.ReadConfig("WaitHack_MaxMonsters")))
		self.SpeedSlider.SetSliderPos(float(FileManager.ReadConfig("WaitHack_Speed")))
		self.RangeSlider.SetSliderPos(float(FileManager.ReadConfig("WaitHack_Range")))
		self.cloudBtn.SetValue(boolean(FileManager.ReadConfig("WaitHack_CloudExploit")))
		self.attackPlayerBtn.SetValue(boolean(FileManager.ReadConfig('WaitHack_attackPlayer')))
		self.playerClose.SetValue(boolean(FileManager.ReadConfig("WaitHack_PlayerClose")))
	
	def saveSettings(self):
		FileManager.WriteConfig("WaitHack_MaxMonsters", str(self.MonsterSlider.GetSliderPos()))
		FileManager.WriteConfig("WaitHack_Speed", str(self.SpeedSlider.GetSliderPos()))
		FileManager.WriteConfig("WaitHack_Range", str(self.RangeSlider.GetSliderPos()))
		FileManager.WriteConfig("WaitHack_PlayerClose", str(self.playerClose.isOn))
		FileManager.WriteConfig("WaitHack_attackPlayer", str(self.attackPlayerBtn.isOn))
		FileManager.WriteConfig("WaitHack_CloudExploit", str(self.cloudBtn.isOn))

		FileManager.Save()
	
	
	def Monster_func(self):
		self.maxMonster = int(self.MonsterSlider.GetSliderPos()*1000)
		self.monsterNum.SetText(str(self.maxMonster))
  
	def Range_func(self):
		self.range = int(self.RangeSlider.GetSliderPos()*10000)
		self.rangeNum.SetText(str(self.range))
	
	def Speed_func(self):
		self.speed = float(self.SpeedSlider.GetSliderPos())
		self.speedNum.SetText(str(int(self.speed*1000)) + ' ms')

	def OnOffBtnState(self,val):
		if(val):
			eXLib.BlockAttackPackets()
		else:
			eXLib.UnblockAttackPackets()
	
	
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
			if OpenLib.dist(x,y,mob_x,mob_y) < OpenLib.ATTACK_MAX_DIST_NO_TELEPORT:
				#chat.AppendChat(3,"Sent Attack, X:" + str(mob_x) + " Y:" + str(mob_y) + "VID: " +str(vid))
				eXLib.SendAttackPacket(vid,0)
				lst.remove(vid)
				vid_hits+=1
		
		return vid_hits
		#chat.AppendChat(3,"After: " + str(len(lst)))

	def __sendUseSkill(self):
		Dmg.cloudSkillState = CLOUD_SKILL_STATE_READY

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

	
	def AttackCloud(self,lst,x,y):
		#chat.AppendChat(3,"Attacking with arch")
		Movement.TeleportStraightLine(self.lastPos[0],self.lastPos[1],x,y)
		self.lastPos = (x,y)
		#eXLib.SendStatePacket(x,y,0,eXLib.CHAR_STATE_STOP,0)
		vid_hits = 0
		for vid in lst:
			mob_x, mob_y, mob_z = chr.GetPixelPosition(vid)
			if OpenLib.dist(x,y,mob_x,mob_y) < OpenLib.ATTACK_MAX_DIST_NO_TELEPORT:
				if not player.IsSkillCoolTime(5) and player.GetStatus(player.SP) >  OpenLib.GetSkillManaNeed(35,5):
					if self.cloudSkillState == CLOUD_SKILL_STATE_READY:
						eXLib.SendUseSkillPacketBySlot(5,vid)
						self.cloudSkillState = CLOUD_SKILL_STATE_USED
					elif self.cloudSkillState == CLOUD_SKILL_STATE_WAITING:
						return 999999999
					else:
						OpenLib.SetTimerFunction(1,self.__sendUseSkill)
						self.cloudSkillState = CLOUD_SKILL_STATE_WAITING
						return 99999999
				x,y,z = chr.GetPixelPosition(vid)
				eXLib.SendAddFlyTarget(vid,x,y)
				eXLib.SendShoot(35)
				lst.remove(vid)
				vid_hits+=1

		return vid_hits
    
				
	def OnUpdate(self):
		val, self.lastTime = OpenLib.timeSleep(self.lastTime,self.speed)
		if(val and self.enableButton.isOn and not eXLib.IsDead(net.GetMainActorVID())):
			if OpenLib.GetCurrentPhase() != OpenLib.PHASE_GAME:
				return
			isArch = OpenLib.IsWeaponArch()
			main_vid = net.GetMainActorVID()
			x,y,z = chr.GetPixelPosition(main_vid)
			self.lastPos = (x,y)
			lst = list()

   			for vid in eXLib.InstancesList:
				if vid == main_vid:
					continue

				if not chr.HasInstance(vid):
					continue

				if self.playerClose.isOn and OpenLib.IsThisPlayer(vid):
					return

				if OpenLib.IsThisNPC(vid):
					continue

				if self.attackPlayerBtn.isOn and OpenLib.IsThisPlayer(vid):
					continue

				if player.GetCharacterDistance(vid) < self.range and not eXLib.IsDead(vid):
					lst.append(vid)
						

			hit_counter = 0
			i = 0
			#chat.AppendChat(3,str(len(lst)))
			while len(lst) > 0 and hit_counter < self.maxMonster:
				vid = lst[0]
				mob_x, mob_y, mob_z = chr.GetPixelPosition(vid)
				if not self.attackBlockedMonsters.isOn:
					if eXLib.IsPositionBlocked(mob_x,mob_y):
						lst.remove(vid)
						continue
				if self.wallBtn.isOn:
					if eXLib.IsPathBlocked(x, y, mob_x, mob_y):
						lst.remove(vid)
						continue
				if self.cloudBtn.isOn and OpenLib.GetClass() == OpenLib.SKILL_SET_DAGGER_NINJA:
					hit_counter+=self.AttackCloud(lst,mob_x, mob_y)
				elif isArch:
					hit_counter+=self.AttackArch(lst,mob_x, mob_y)
				else:
					hit_counter+=self.TeleportAttack(lst,mob_x, mob_y)
				i+=1
			if(OpenLib.dist(x,y,self.lastPos[0],self.lastPos[1]) >=50):
				Movement.TeleportStraightLine(self.lastPos[0], self.lastPos[1], x, y)
	
	def Close(self):
		self.Board.Hide()
		self.saveSettings()

def Pause():
	"""
	Pauses the damage hack.
	"""
	Dmg.enableButton.SetOff()

def Resume():
	"""
	Resumes damage hack.
	"""
	Dmg.enableButton.SetOn()

def IsOn():
	return Dmg.enableButton.isOn

def switch_state():
	"""
	Open's or closes the UI window.
	"""
	Dmg.OpenWindow()

Dmg = DmgHacksInstance()
Dmg.Show()