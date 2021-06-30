import Movement
import ui,OpenLib,NPCInteraction,DmgHacks,player,Settings,chat,OpenLog
import abc
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


	def __init__(self,time_wait=0.1,shopOnFullInv = False):
		"""Constructor

		Args:
			time_wait (float, optional): Time between frame calls, in seconds. Defaults to 0.06.
			shopOnFullInv (bool, optional): If True it will go to shop when inventory full. Defaults to False.
		"""
		__metaclass__ = abc.ABCMeta
		ui.ScriptWindow.__init__(self)
		self.Show()
		self.State = self.STATE_STOPPED
		self.time_wait = time_wait
		self.generalTimer = 0

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
		
###########################
####Abstract Functions######
###########################
	@abc.abstractmethod
	def Frame(self):
		"""Function called repeateadly to preform bot functions.
		The delay between calls can be changed by calling ChangeTimeDelay or on constructor.
		This function is not called when the bot is stopped and MUST be redifined in the super class.
		"""
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
#########################


	def OnUpdate(self):
		if self.STATE_STOPPED == self.State:
			return

		val, self.generalTimer = OpenLib.timeSleep(self.generalTimer,self.time_wait)
		if not val:
			return

		if OpenLib.GetCurrentPhase() != OpenLib.PHASE_GAME:
			return

		if self.State == self.STATE_WATING:
			return

		if not self.DoChecks():		
			self.Frame()
