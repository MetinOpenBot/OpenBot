import game,sys,chat,net
import functools

"""
Hooking module.
"""

#The current phase.
CURRENT_PHASE = 2

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
	global CURRENT_PHASE
	if len(args)>1 and args[1] != 0:
		CURRENT_PHASE = args[0]
	phaseHook.CallOriginalFunction(*args,**kwargs)


class SkipHook(Hook):
	def __init__(self,toHookFunc):
		Hook.__init__(self,toHookFunc,skipFunc)



debugFunc = 0
questHook = SkipHook(game.GameWindow.OpenQuestWindow)
phaseHook = Hook(net.SetPhaseWindow,phaseIntercept)

def GetQuestHookObject():
	return questHook


def GetCurrentPhase():
	global CURRENT_PHASE
	return CURRENT_PHASE

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


#Print arguments of a function
def _debugHookFunctionArgs(func):
	global debugFunc
	debugFunc = Hook(func,printFunc)
	debugFunc.HookFunction()

def _debugUnhookFunctionArgs():
	debugFunc.UnhookFunction()


phaseHook.HookFunction()