import game,sys,chat,net, player, item
import functools
import OpenLog

"""
Hooking module.
"""

#The current phase.
CURRENT_PHASE = 5
phaseCallbacks = {}
GAME_WINDOW = 0

class Hook():
	"""
	Hook class that allows to replace functions in modules.
	"""
	def __init__(self,toHookFunc,replaceFunc):
		self.originalFunc = toHookFunc
		self.replaceFunc = replaceFunc
		self.functionName = str(toHookFunc.__name__)
		self.functionOwner = self.GetFunctionOwner(toHookFunc)
		self.isHooked = False



	def GetFunctionOwner(self,func):
		"""
		Return the object owner of the function 

		Args:
			func ([function]): a function.

		Returns:
			[object]: Return the object owner of the function.
		"""
		try:
			owner = func.im_class		#In case of a class function
		except AttributeError:
			owner = sys.modules[func.__module__]
		
		return owner


	def CallOriginalFunction(self,*args,**kwargs):
		"""
		Call the original function before the hook.
		Returns:
			[args]: the arguments of the function.
		"""
		@functools.wraps(self.originalFunc)
		def run(*args, **kwargs):
			return self.originalFunc(*args, **kwargs)
		return run(*args,**kwargs)
		
	def HookFunction(self):
		"""
		Hook the function.
		"""
		if self.isHooked:
			return
		self.isHooked = True
		setattr(self.functionOwner, self.functionName, self.replaceFunc)

	def UnhookFunction(self):
		"""
		Remove the hook and put the original function.
		"""
		if self.isHooked == False:
			return
		self.isHooked = False
		#chat.AppendChat(3,"Function Owner: " + str(self.functionOwner.__name__) + "Function Name: " + str(self.functionName))
		setattr(self.functionOwner, self.functionName, self.originalFunc)

def skipFunc(*args):
	"""
	Function that doesn nothing.
	"""
	pass 

def phaseIntercept(*args,**kwargs):
	#printFuncNC(*args,**kwargs)
	global CURRENT_PHASE
	if len(args)>1 and args[1] != 0:
		CURRENT_PHASE = args[0]
	OpenLog.DebugPrint("PHASE: "+ str(CURRENT_PHASE))
	for callback_id in phaseCallbacks:
		callback = phaseCallbacks[callback_id]
		if callable(callback):
			callback(CURRENT_PHASE,args[1])
	phaseHook.CallOriginalFunction(*args,**kwargs)

def registerPhaseCallback(id,func):
	phaseCallbacks[id] = func

def deletePhaseCallback(id):
	if id in phaseCallbacks:
		del phaseCallbacks[id]

class SkipHook(Hook):
	def __init__(self,toHookFunc):
		Hook.__init__(self,toHookFunc,skipFunc)


def GameWindowIntercept(*args,**kwargs):
	#This is supposed to be run One Time, after this you can access "Current Window attribute from stream."
	import Hooks, Data, player
	if args[0] == 0:
		return
	#printFuncNC(*args,**kwargs)
	Data.GameWindow = args[0]
	Data.obj = Data.uiShortcut() #The Constructor resets player.SetGameWindow to original method thus removing the hook. 
	Hooks.GAME_WINDOW = args[0]
	player.SetGameWindow(*args, **kwargs)


def CheckAffectIntercept(*args,**kwargs):
    import Hooks, chr
    #printFuncNC(*args,**kwargs)
    if args[0] == chr.NEW_AFFECT_AUTO_USE:
            #chat.AppendChat(7,"Returned True for Auto Use")
            return True
    else:
        Hooks.checkAffectHook.CallOriginalFunction(*args, **kwargs)

debugFunc = 0
questHook = SkipHook(game.GameWindow.OpenQuestWindow)
phaseHook = Hook(net.SetPhaseWindow,phaseIntercept)
gameWindowHook = Hook(player.SetGameWindow, GameWindowIntercept)
checkAffectHook = Hook(item.CheckAffect, CheckAffectIntercept)

def GetQuestHookObject():
	return questHook


def GetCurrentPhase():
	global CURRENT_PHASE
	return CURRENT_PHASE

def GetGameWindow():
	global GAME_WINDOW
	return GAME_WINDOW

def printFunc(*args,**kwargs):
	"""
	Print the arguments of a function to a debug.txt file.(In the game folder)
	"""
	with open("debug.txt","a") as f:
		#chat.AppendChat(3,"[DebugHook] Function called arguments:")
		f.write("[DebugHook] Function called arguments:\n")
		for i,arg in enumerate(args):
			f.write("[DebugHook] Arg "+ str(i) + ": "+ str(arg)+"\n")
			#chat.AppendChat(3,"[DebugHook] Arg "+ str(i) + ": "+ str(arg))
		f.write("\n")
	debugFunc.CallOriginalFunction(*args,**kwargs)

def printFuncNC(*args,**kwargs):
	"""
	Print the arguments of a function to a debug.txt file.(In the game folder)
	This happens without Calling the Original.
	"""
	with open("debug.txt","a") as f:
		#chat.AppendChat(3,"[DebugHook] Function called arguments:")
		f.write("[DebugHook] Function called arguments:\n")
		for i,arg in enumerate(args):
			f.write("[DebugHook] Arg "+ str(i) + ": "+ str(arg)+"\n")
			#chat.AppendChat(3,"[DebugHook] Arg "+ str(i) + ": "+ str(arg))
		f.write("\n")

#Print arguments of a function
def _debugHookFunctionArgs(func):
	global debugFunc
	debugFunc = Hook(func,printFunc)
	debugFunc.HookFunction()

def _debugUnhookFunctionArgs():
	debugFunc.UnhookFunction()

phaseHook.HookFunction()
gameWindowHook.HookFunction()
checkAffectHook.HookFunction()