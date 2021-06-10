import ui
import dbg
import app
import OpenLib
import eXLib
import chat
import UIComponents

class PythonManagerDialog(ui.Window):
	def __init__(self):
		ui.Window.__init__(self)
		self.BuildWindow()

	def __del__(self):
		ui.Window.__del__(self)

	def BuildWindow(self):
		self.Board = ui.BoardWithTitleBar()
		self.Board.SetSize(448, 130)
		self.Board.SetPosition(52, 40)
		self.Board.AddFlag('movable')
		self.Board.AddFlag('float')
		self.Board.SetTitleName('Python File Loader')
		self.Board.SetCloseEvent(self.Board.Hide)
		self.Board.Hide()
		self.comp = UIComponents.Component()

		self.loadFileButton = self.comp.Button(self.Board, 'Load File', '', 341, 61, self.loadFile, 'd:/ymir work/ui/public/large_button_01.sub', 'd:/ymir work/ui/public/large_button_02.sub', 'd:/ymir work/ui/public/large_button_03.sub')
		self.slotbar_file, self.fileEditBox = self.comp.EditLine(self.Board, 'file.py', 24, 63, 310, 15, 60)
		self.text8 = self.comp.TextLine(self.Board, 'Python File Loader', 179, 41, self.comp.RGB(255, 255, 0))
  		self.text9 = self.comp.TextLine(self.Board, 'Note: File has to be at the same location as the injector', 28, 81, self.comp.RGB(255, 255, 255))

	def loadCMD(self):
		exec(self.loadCMD.GetText())
	
	def loadFile(self):
		f = open(str(eXLib.PATH)+self.fileEditBox.GetText(),"r")
		exec(f.read())
		f.close()
	
	def __BuildKeyDict(self):
		onPressKeyDict = {}
		onPressKeyDict[app.DIK_F5]	= lambda : self.OpenWindow()
		self.onPressKeyDict = onPressKeyDict

	def switch_state(self):
		if self.Board.IsShow():
			self.Board.Hide()
		else:
			self.Board.Show()
	
	def OnKeyDown(self, key):
		try:
			self.onPressKeyDict[key]()
		except KeyError:
			pass
		except:
			raise
		return True
	
	def OpenWindow(self):
		if self.Board.IsShow():
			self.Board.Hide()
		else:
			self.Board.Show()
	
	def Close(self):
		self.Board.Hide()
