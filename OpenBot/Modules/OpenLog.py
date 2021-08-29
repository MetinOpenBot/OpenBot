from datetime import datetime
import eXLib

def DebugPrint(arg):
	"""
	Log's information to Log.txt file.

	Args:
		arg ([str]): Information to log.
	"""
	with open(eXLib.PATH+"\\Log.txt","a") as f:
		f.write(str(datetime.now())+": "+arg+"\n")
	pass

def handleRequest(id,msg):
    DebugPrint(msg)

#To override the file
f = open(eXLib.PATH+"\\Log.txt","w")
f.close()