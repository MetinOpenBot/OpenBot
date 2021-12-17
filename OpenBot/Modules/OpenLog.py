from datetime import datetime
import eXLib

def DebugPrint(arg):
	"""
	Log's information to Log.txt file.

	Args:
		arg ([str]): Information to log.
	"""
	with open(eXLib.PATH+"\\Log.txt","a") as f:
		f.write(str(datetime.now())+": "+str(arg)+"\n")
	pass

def DebugPrintNT(arg):
	"""
	Log's information to Log.txt file. This will Not print time.

	Args:
		arg ([str]): Information to log.
	"""
	with open(eXLib.PATH+"\\Log.txt","a") as f:
		f.write(str(arg)+"\n")
	pass

def DumpObject(arg):
	with open(eXLib.PATH+"\\ObjectDump.txt","w") as f:
		for i in arg.__dict__:
			f.write(str(i) + "\n")

def handleRequest(id,msg):
    DebugPrint(msg)

#To override the file
f = open(eXLib.PATH+"\\Log.txt","w")
f.close()