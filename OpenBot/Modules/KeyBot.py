import UIComponents, Data
from BotBase import BotBase
import ui, player, app, chat, eXLib
import OpenLib, FileManager, OpenLog, Hooks
from OpenBot.Modules.Actions import ActionBot
"""
  app.DIK_0: {'function': None},
            app.DIK_1: {'function': None},
            app.DIK_2: {'function': None},
            app.DIK_3: {'function': None},
            app.DIK_4: {'function': None},
            app.DIK_5: {'function': None},
            app.DIK_6: {'function': None},
            app.DIK_7: {'function': None},
            app.DIK_8: {'function': None},
            app.DIK_9: {'function': None},
            app.DIK_A: {'function': None},
            app.DIK_ADD: {'function': None},
            app.DIK_APOSTROPHE: {'function': None},
            app.DIK_APPS: {'function': None},
            app.DIK_B: {'function': None},
            app.DIK_BACK: {'function': None},
            app.DIK_BACKSLASH: {'function': None},
            app.DIK_C: {'function': None},
            app.DIK_CALCULATOR: {'function': None},
            app.DIK_CAPITAL: {'function': None},
            app.DIK_COMMA: {'function': None},
            app.DIK_D: {'function': None},
            app.DIK_DECIMAL: {'function': None},
            app.DIK_DELETE: {'function': None},
            app.DIK_DIVIDE: {'function': None},
            app.DIK_DOWN: {'function': None},
            app.DIK_E: {'function': None},
            app.DIK_END: {'function': None},
            app.DIK_EQUALS: {'function': None},
            app.DIK_ESC: {'function': None},
            app.DIK_ESCAPE: {'function': None},
            app.DIK_F: {'function': None},
            app.DIK_F1: {'function': None},
            app.DIK_F2: {'function': None},
            app.DIK_F3: {'function': None},
            app.DIK_F4: {'function': None},
  app.DIK_F10: {'function': None},
            app.DIK_F11: {'function': None},
            app.DIK_F12: {'function': self.SwitchDmgHack},
            app.DIK_G: {'function': None},
            app.DIK_GRAVE: {'function': None},
            app.DIK_H: {'function': None},
            app.DIK_HOME: {'function': None},
            app.DIK_I: {'function': None},
            app.DIK_INSERT: {'function': None},
            app.DIK_J: {'function': None},
            app.DIK_K: {'function': None},
            app.DIK_L: {'function': None},
            app.DIK_LALT: {'function': None},
            app.DIK_LBRACKET: {'function': None},
            app.DIK_LCONTROL: {'function': None},
            app.DIK_LEFT: {'function': None},
            app.DIK_LSHIFT: {'function': None},
            app.DIK_LWIN: {'function': None},
            app.DIK_M: {'function': None},
            app.DIK_MEDIASTOP: {'function': None},
            app.DIK_MINUS: {'function': None},
            app.DIK_MULTIPLY: {'function': None},
            app.DIK_MUTE: {'function': None},
            app.DIK_N: {'function': None},
            app.DIK_NEXTTRACK: {'function': None},
            app.DIK_NUMLOCK: {'function': None},
            app.DIK_NUMPAD0: {'function': None},
            app.DIK_NUMPAD1: {'function': None},
            app.DIK_NUMPAD2: {'function': None},
            app.DIK_NUMPAD3: {'function': None},
            app.DIK_NUMPAD4: {'function': None},
            app.DIK_NUMPAD5: {'function': None},
            app.DIK_NUMPAD6: {'function': None},
            app.DIK_NUMPAD7: {'function': None},
            app.DIK_NUMPAD8: {'function': None},
            app.DIK_NUMPAD9: {'function': None},
            app.DIK_NUMPADCOMMA: {'function': None},
            app.DIK_NUMPADENTER: {'function': None},
            app.DIK_O: {'function': None},
            app.DIK_P: {'function': None},
            app.DIK_PAUSE: {'function': None},
            app.DIK_PERIOD: {'function': None},
            app.DIK_PGDN: {'function': None},
            app.DIK_PGUP: {'function': None},
            app.DIK_PLAYPAUSE: {'function': None},
            app.DIK_PLAYPAUSE: {'function': None},
            app.DIK_Q: {'function': None},
            app.DIK_R: {'function': None},
            app.DIK_RALT: {'function': None},
            app.DIK_RBRACKET: {'function': None},
            app.DIK_RCONTROL: {'function': None},
            app.DIK_RETURN: {'function': None},
            app.DIK_RIGHT: {'function': None},
            app.DIK_RSHIFT: {'function': None},
            app.DIK_RWIN: {'function': None},
            app.DIK_SCROLL: {'function': None},
            app.DIK_SEMICOLON: {'function': None},
            app.DIK_SLASH: {'function': None},
            app.DIK_SPACE: {'function': None},
            app.DIK_SUBTRACT: {'function': None},
            app.DIK_SYSRQ: {'function': None},
            app.DIK_T: {'function': None},
            app.DIK_TAB: {'function': None},
            app.DIK_U: {'function': None},
            app.DIK_UP: {'function': None},
            app.DIK_V: {'function': None},
            app.DIK_VOLUMEDOWN: {'function': None},
            app.DIK_VOLUMEUP: {'function': None},
            app.DIK_W: {'function': None},
            app.DIK_WEBHOME: {'function': None},
            app.DIK_X: {'function': None},
            app.DIK_Y: {'function': None},
            app.DIK_Z: {'function': None},}
"""
def _afterLoadPhase(phase,phaseWnd):
    global instance
    if phase == OpenLib.PHASE_LOGIN or phase == OpenLib.PHASE_GAME:
        instance.enableButton.SetOn()
        instance.Start()

class Keybot(BotBase):

    def __init__(self):
        BotBase.__init__(self)
        self.canPress = True
        self.keys = {
            app.DIK_F5: {'function': self.SwitchDmgHack},
            app.DIK_F6: {'function': self.SwitchFarmBot},
            app.DIK_F7: {'function': self.SwitchAutoLogin},
            app.DIK_F8: {'function': self.SwitchPickUp},
            app.DIK_F9: {'function': self.SwitchActionBot},
        }
        self.BuildWindow()

    def BuildWindow(self):

        self.comp = UIComponents.Component()
        self.Board = ui.ThinBoard()
        self.Board.SetSize(235, 150)
        self.Board.SetPosition(52, 40)
        self.Board.AddFlag('movable')
        self.Board.Hide()
        self.comp = UIComponents.Component()
        self.enableButton = self.comp.OnOffButton(self.Board, '', '', 15, 40,
                                                  OffUpVisual=eXLib.PATH + 'OpenBot/Images/start_0.tga',
                                                  OffOverVisual=eXLib.PATH + 'OpenBot/Images/start_1.tga',
                                                  OffDownVisual=eXLib.PATH + 'OpenBot/Images/start_2.tga',
                                                  OnUpVisual=eXLib.PATH + 'OpenBot/Images/stop_0.tga',
                                                  OnOverVisual=eXLib.PATH + 'OpenBot/Images/stop_1.tga',
                                                  OnDownVisual=eXLib.PATH + 'OpenBot/Images/stop_2.tga',
                                                  funcState=self._start, defaultValue=False)

        self.text_line1 = self.comp.TextLine(self.Board, 'F5 to switch WaitHack', 70, 30, self.comp.RGB(255, 255, 255))
        self.text_line2 = self.comp.TextLine(self.Board, 'F6 to switch FarmBot', 70, 50, self.comp.RGB(255, 255, 255))
        self.text_line3 = self.comp.TextLine(self.Board, 'F7 to switch AutoLogin', 70, 70, self.comp.RGB(255, 255, 255))
        self.text_line4 = self.comp.TextLine(self.Board, 'F8 to switch Pickup', 70, 90, self.comp.RGB(255, 255, 255))
        self.text_line5 = self.comp.TextLine(self.Board, 'F9 to switch ActionBot', 70, 110, self.comp.RGB(255, 255, 255))
                                
    
    def _start(self, val):
        if val:
            self.Start()
        else:
            self.Stop()

    def Frame(self):
        if self.canPress:
            for key in self.keys.keys():
                if app.IsPressed(key):
                    if self.keys[key]['function'] != None:
                        self.keys[key]['function']()
                        self.canPress = False
        else:
            
            val, Data.time_KeyBot_timerBlock = OpenLib.timeSleep(Data.time_KeyBot_timerBlock,2) #Avoid multiple calls on same keypress
            if val:
                self.canPress = True
    
    def switch_state(self):
        if self.Board.IsShow():
            self.Board.Hide()
        else:
            self.Board.Show()

    # KEYS FUNCTION 
    def SwitchDmgHack(self):
        from OpenBot.Modules import DmgHacks 
        if DmgHacks.IsOn():
            DmgHacks.Pause()
        else:
            DmgHacks.Resume()

    def SwitchFarmBot(self):
        from OpenBot.Modules import FarmingBot
        if FarmingBot.farm.enableButton.isOn:
            FarmingBot.farm.enableButton.SetOff()
        else:
            FarmingBot.farm.enableButton.SetOn()

    def SwitchAutoLogin(self):
        from OpenBot.Modules import Settings
        if Settings.instance.loginBtn.isOn:
            Settings.instance.loginBtn.SetOff()
        else:
            Settings.instance.loginBtn.SetOn()

    def SwitchPickUp(self):
        from OpenBot.Modules import Settings
        if Settings.instance.pickupButton.isOn:
            Settings.instance.pickupButton.SetOff()
        else:
            Settings.instance.pickupButton.SetOn()

    def SwitchActionBot(self):
        from OpenBot.Modules.Actions import ActionBot
        if ActionBot.instance.enableActionBot.isOn:
            ActionBot.instance.enableActionBot.SetOff()
        else:
            ActionBot.instance.enableActionBot.SetOn()


def switch_state():
    instance.switch_state()

instance = Keybot()
Hooks.registerPhaseCallback("skillCallback", _afterLoadPhase)