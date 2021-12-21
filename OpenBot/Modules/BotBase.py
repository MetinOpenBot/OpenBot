import Movement
import ui,OpenLib,NPCInteraction,DmgHacks,player,Settings,chat,OpenLog,Settings, Data
import abc
from .Actions import ActionRequirementsCheckers

class BotBase(ui.ScriptWindow):
	""" 
	Base class for a bot mode.
	Automatically handles auto shop buy (if specified) and maybe others in the future.
	The Frame need to be redefined in the superclass, this is the method called repeatedly and it's responsible for preforming the bot actions 
	Whenever some process needs to be ran in this class and it needs the bot to be stopped (like going to shop and comeback),
	it will first call CanPause and only if it returns True it will Pause the bot by not calling the method Frame, when the process is completed the Resume
	function will be called and the bot will resume it's operation trough the Frame.
	The CanPause, Pause, Resume, StartBot and StopBot functions can be redefined in the superclass in order to prefmore specific actions.
	DO NOT REDEFINE THE METHODS: OnUpdate, Start or Stop
	"""
	STATE_STOPPED = 0
	STATE_BOTTING = 1
	#STATE_GOING_SHOP = 2
	STATE_WATING = 3


	def __init__(self,time_wait=0.1,shopOnFullInv = False,onlyGamePhase=True,waitIsPlayerDead=False):
		"""Constructor

		Args:
			time_wait (float, optional): Time between frame calls, in seconds. Defaults to 0.06.
			shopOnFullInv (bool, optional): If True it will go to shop when inventory full. Defaults to False.
			onlyGamePhase (bool,optional): The same as SetOnlyGamePhase
			waitIsPlayerDead (bool,optional): The same as SetWaitPlayerIsDead
		"""
		__metaclass__ = abc.ABCMeta

		self.currSchema = None
		self.currStage = 0
		self.currAction = 0
		self.isCurrActionDone = True
		ui.ScriptWindow.__init__(self)
		self.Show()
		self.State = self.STATE_STOPPED
		self.time_wait = time_wait
		Data.time_BotBase_generalTimers[self.__class__.__name__] = 0
		self.timer = Data.time_BotBase_generalTimers
		self.name = self.__class__.__name__
		self.onlyGamePhase = onlyGamePhase
		self.waitIsPlayerDead = waitIsPlayerDead
		self.isPaused = False



		#Shop - Can be changed using callback by super class
		self.onInvFullCallback = None #Will call this function before going to shop
		self.allowShopOnFullInv = shopOnFullInv #Allow to go to shop when inventory full

		self.shopBuySlots = set() #This items SLOTS will be bought when going to shop
		self.shopSellSlots = set() #This items SLOTS will be sold when going to shop

	#DO NOT CALL THIS FUNCTIONS FROM SUPER CLASSES
	def __SetStateBotting(self):
		self.State = self.STATE_BOTTING
		#DmgHacks.Resume()
		self.Resume()

	def __SetStateStopped(self):
		self.State = self.STATE_STOPPED
		#DmgHacks.Resume()
		NPCInteraction.StopAction()
		self.Pause()

	def __SetStateShopping(self):
		OpenLog.DebugPrint("[BotBase] Shopping")
		self.State = self.STATE_WATING
		#DmgHacks.Pause()
		self.Pause()

	def _ResumeCallback(self):
		OpenLog.DebugPrint("[BotBase] Resuming bot")
		self.__SetStateBotting()

	def SetOnlyGamePhase(self,onlyGame):
		self.onlyGamePhase = onlyGame

	def GoToShop(self):
		if self.onInvFullCallback != None:
			self.onInvFullCallback()
		self.__SetStateShopping()
		to_sell = self.shopSellSlots.union(Settings.GetSlotItemsToSell())
		NPCInteraction.RequestBusinessNPCAwayRestorePosition(self.shopBuySlots,to_sell,NPCInteraction.GetGeneralShop(),callback=self._ResumeCallback)

	#Preform checks
	def DoChecks(self):
		if self.allowShopOnFullInv and OpenLib.isInventoryFull() and self.CanPause():
			self.GoToShop()
			return True

		if self.waitIsPlayerDead:
			last_time_dead, time_wait = Settings.GetLastTimeDead()
			if(last_time_dead+time_wait>OpenLib.GetTime()):
				if(self.CanPause() and not self.isPaused):
					self.isPaused = True
					self.Pause()
				return True
			if(self.isPaused):
				self.isPaused = False
				self.Resume()
		return False
	

###################
	#Setters
###################
	#Enable to go shop on inventory full
	def	SetShopOnInvFull(self,value,callback=None):
		"""Enable/Disable to go shop on inventory full.
		Args:
			value ([bool]): If True it will go to shop when inventory full. 
			callback ([function], optional): Callback to be called after the player returned from shop. Defaults to None.
		"""
		self.allowShopOnFullInv = value
		if self.onInvFullCallback == None:
			self.onInvFullCallback = callback

	#Allow to change the time delay
	def ChangeTimeDelay(self,this_time):
		"""
		Change the time delay between frames.

		Args:
			this_time ([float]): Delay in seconds.
		"""
		self.time_wait = this_time

	def SetOnlyGamePhase(self,onlyGame):
		"""
		Sets the frame to be run either only on game phase or on all phases.

		Args:
			onlyGame ([boolean]): If True, Frame will only be ran in Game phase otherwise will be ran in all phases.
		"""
		self.onlyGamePhase = onlyGame

	def SetWaitPlayerIsDead(self,waitAfterDead):
		"""
		Sets the frame to not be run a specified time in settings after it died.

		Args:
			waitAfterDead ([boolean]): If True, Frame will not be ran on the next x seconds defined in Settings.
		"""
		self.waitIsPlayerDead = waitAfterDead

	def Start(self):
		"""
		Starts the bot.
		"""
		self.StartBot()
		self.__SetStateBotting()

	def Stop(self):
		"""Stops the bot.
		"""
		self.StopBot()
		self.__SetStateStopped()
		NPCInteraction.StopAction()
		self.currSchema = None
		self.currStage = 0
		self.currAction = 0
		self.isCurrActionDone = True
	
	def CheckRequirementsForCurrSchema(self):
		for requirement in self.currSchema['requirements'].keys():
			if requirement == 'lvl':
				if not ActionRequirementsCheckers.isAboveLVL(self.currSchema['requirements'][requirement]):
					chat.AppendChat(3, '[BotBase] You have ' + str(player.GetStatus(player.LEVEL)) + ' lvl but you need ' + str(self.currSchema['requirements'][requirement]))
					return False

			if requirement == 'inInMap':
				if not ActionRequirementsCheckers.isInMaps(self.currSchema['requirements'][requirement]):
					chat.AppendChat(3, '[BotBase] You need to be atleast on this maps: ' + str(self.currSchema['requirements'][requirement]))
					return False
            
			if requirement == 'isOnPosition':
				if not ActionRequirementsCheckers.inOnPosition(self.currSchema['requirements'][requirement]):
					chat.AppendChat(3, '[BotBase] You need to be on this position: ' + str(self.currSchema['requirements'][requirement]))
					return False
        
		return True

	def SetIsCurrActionDoneTrue(self):
		self.GoToNextAction()
		self.isCurrActionDone = True

	def GoToNextAction(self):
		if self.currSchema != None:
			if self.currAction + 1 < len(self.currSchema['stages'][self.currStage]['actions']):
				self.currAction += 1
			else:
				if 'options' in self.currSchema['stages'][self.currStage].keys():
					if 'stage_reapat' in self.currSchema['stages'][self.currStage]['options']:
						self.currAction = 0
						return
				OpenLog.DebugPrint('Stage Complete')
				self.GoToNextStage()

	def GoToNextStage(self):
		self.currAction = 0
		if self.currStage + 1 < len(self.currSchema['stages']):
			if 'options' in self.currSchema['stages'][self.currStage].keys():
				if 'stage_reapat' in self.currSchema['stages'][self.currStage]['options']:
					return

			self.currStage += 1
		else:
			if 'options' in self.currSchema['stages'][self.currStage].keys():
				if 'repeatDungeon' in self.currSchema['stages'][self.currStage]['options']:
					if self.currSchema['stages'][self.currStage]['options']['repeatDungeon']:
						self.currSchema['stages'][self.currStage]['options']['CountRepeat'] += 1
						if self.currSchema['stages'][self.currStage]['options']['CountRepeat'] > self.currSchema['stages'][self.currStage]['options']['HowMuchRepeat']:
							OpenLog.DebugPrint('Dungeon Complete')
							self.Stop()
						else:
							self.currStage = self.RecognizeStageBot()
			OpenLog.DebugPrint('Dungeon Complete')
			self.Stop()			
			
###########################
####Abstract Functions######
###########################
	@abc.abstractmethod
	def Frame(self):
		"""Function called repeateadly to preform bot functions.
		The delay between calls can be changed by calling ChangeTimeDelay or on constructor.
		This function is not called when the bot is stopped and MUST be redifined in the super class.
		"""
		#chat.AppendChat(7, "Wrong Frame is running! ")
		#chat.AppendChat(7, "Self Obj: " + str(self))
		pass

	def CanPause(self):
		"""Function called to check if the bot can be stopped.
		Must return True if it can and must return False if it can't.
		"""
		return True

	def Resume(self):
		"""Function called everytime the bot is resumed.
		"""
		return True

	def Pause(self):
		"""Function called everytime the bot is paused.
		"""
		pass

	def StartBot(self):
		"""Function called when the bot is started.
		"""
		return

	def StopBot(self):
		"""Function called when the bot is stopped.
		"""
		return
	
	def RecognizeStageBot(self):
		return 0
#########################


	def OnUpdate(self):
		if self.STATE_STOPPED == self.State:
			return
		val, self.timer[self.name] = OpenLib.timeSleep(self.timer[self.name],self.time_wait)
		if not val:
			return
		if OpenLib.GetCurrentPhase() != OpenLib.PHASE_GAME and self.onlyGamePhase:
			return

		if self.State == self.STATE_WATING:
			return
		if not self.DoChecks():
			#chat.AppendChat(7,str(self.timer[self.name])+" Self.Timer from " + self.name) #Debug
			#chat.AppendChat(7,str(Data.time_BotBase_generalTimers[self.name])+ " Data.Timer from " + self.name)
			self.Frame()
