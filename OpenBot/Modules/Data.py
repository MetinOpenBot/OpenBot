import eXLib, ui, OpenThreads
import UIComponents, Hooks
"""Class for Persistant Data Exchange + permanent ON/OFF UIs with Hotkeys"""

obj = 0
GameWindow = 0
stream = 0

########
# Persistant Vars
# Updated Once Per Game Phase. 

mainVID = 0             # Own unique ID 
empireID = 0            # Own selected Empire
mainSkillGroup = 0      # Character Skill group
mainRace = 0            # Character gender and type (ninja, warrior, shaman , sura, lycan)
serverInfo = 0          # Server Info with Server IDs, IPs, Ports and other data


## TMP - Unused, preparation for future version. TODO add Implementation

waithackState   = 0
pickupState     = 0
mobOnClickState = 0
farmbotState    = 0
fishbotState    = 0
keybotState     = 0

########
# Timers used in Bot 
# Naming: "time_[Bot-Module]_[varName]"

time_BotBase_generalTimers   = {}
time_DmgHacks_lastcloud     = 0
time_DmgHacks_lastpotion    = 0
time_DmgHacks_lasttime      = 0
time_FarmingBot_lastTimeWaitingState= 0
time_FishingBot_lasttime    = 0
time_FishingBot_lastTimeWaitState   = 0
time_FishingBot_lastTimeFishState   = 0
time_FishingBot_lastTimeImprove     = 0
time_FishingBot_lastTimeFire        = 0
time_InventoryManager_lasttime      = 0
time_KeyBot_timerBlock        = 0
time_Movement_generalTimer  = 0
time_Movement_stoppedTimer  = 0
time_NPCInteraction_lastTime= 0
time_NPCInteraction_lastTimeSell    = 0
time_NPCInteraction_lastTimeBuy     = 0
time_NPCInteraction_lastTimeGive    = 0
time_Radar_lastTimeClearedList      = 0
time_Settings_timerDmg      = 0
time_Settings_timerPots     = 0
time_Settings_timerDead     = 0
time_Settings_pickUpTimer   = 0
time_Skillbot_startUpWaitTime       = 0
time_Telehack_timerBlock    = 0





#SetButtonScale('self', 'xScale', 'yScale')


class uiShortcut(ui.ScriptWindow):
    
    comp = UIComponents.Component()
    def __init__(self):
        ui.ScriptWindow.__init__(self)
        Hooks.gameWindowHook.UnhookFunction()
        OpenThreads.threadInstance.createThread(self.aquireStream,())

        """
        TODO WIP

        Shortcutboard, to quickaccess Start/Stop Buttons, including Hotkeys
        
        self.ShortcutBoard = ui.ThinBoard(layer="TOP_MOST")
        self.ShortcutBoard.SetPosition(200,20)
        self.ShortcutBoard.SetSize(400,40)

        self.btnWaithack = self.comp.OnOffButton(self.ShortcutBoard, '', 'Switch Waithack', 10, 5, OffUpVisual=eXLib.PATH + 'OpenBot/Images/start_0.tga', OffOverVisual=eXLib.PATH + 'OpenBot/Images/start_1.tga', OffDownVisual=eXLib.PATH + 'OpenBot/Images/start_2.tga',OnUpVisual=eXLib.PATH + 'OpenBot/Images/stop_0.tga', OnOverVisual=eXLib.PATH + 'OpenBot/Images/stop_1.tga', OnDownVisual=eXLib.PATH + 'OpenBot/Images/stop_2.tga',funcState=self.waithackSwitch)

        self.btnPickup = self.comp.OnOffButton(self.ShortcutBoard, '', 'Switch Pickup', 50, 5, OffUpVisual=eXLib.PATH + 'OpenBot/Images/start_0.tga', OffOverVisual=eXLib.PATH + 'OpenBot/Images/start_1.tga', OffDownVisual=eXLib.PATH + 'OpenBot/Images/start_2.tga',OnUpVisual=eXLib.PATH + 'OpenBot/Images/stop_0.tga', OnOverVisual=eXLib.PATH + 'OpenBot/Images/stop_1.tga', OnDownVisual=eXLib.PATH + 'OpenBot/Images/stop_2.tga',funcState=self.pickupSwitch)

        
        self.btnWaithack.SetButtonScale(0.5,0.5)
        self.btnPickup.SetButtonScale(0.5,0.5)

        """

        #self.ShortcutBoard.Show()


    # Get Stream Variable to Access Game Data. 
    def aquireStream(args):
        import Data, time, chat
        
        time.sleep(2)

        while Data.GameWindow == 0:
            time.sleep(1)
        
        while Data.stream == 0:
            time.sleep(1)
            Data.stream = getattr(Data.GameWindow, "stream",0)
        chat.AppendChat(7, "Stream Aquired")


    def waithackSwitch(self,state):
        import DmgHacks
        if state:
            DmgHacks.Resume()
        else:
            DmgHacks.Pause()

    def waithackHotkeyPressed(self):
        if self.btnWaithack.IsOn:
            self.btnWaithack.SetOff()
        else:
            self.btnWaithack.SetOn()

    def pickupSwitch(self,state):
        import Settings
        if state:
            Settings.instance.pickupButton.SetOn()
        else:
            Settings.instance.pickupButton.SetOff()

    def PickupHotkeyPressed(self):
        if self.btnPickup.IsOn:
            self.btnPickup.SetOff()
        else:
            self.btnPickup.SetOn()

    

def resetTimers():
    # Setting most Variables to 5 to block constant Kicks - in case of too high values. 
    import Data
    for key in Data.time_BotBase_generalTimers.keys():
        Data.time_BotBase_generalTimers[key] = 5;
    Data.time_DmgHacks_lastcloud     = 5
    Data.time_DmgHacks_lastpotion    = 5
    Data.time_DmgHacks_lasttime      = 5
    Data.time_FarmingBot_lastTimeWaitingState= 5
    Data.time_FishingBot_lasttime    = 5
    Data.time_FishingBot_lastTimeWaitState   = 5
    Data.time_FishingBot_lastTimeFishState   = 5
    Data.time_FishingBot_lastTimeImprove     = 5
    Data.time_FishingBot_lastTimeFire        = 5
    Data.time_InventoryManager_lasttime      = 5
    Data.time_KeyBot_timerBlock        = 0
    Data.time_Movement_generalTimer  = 5
    Data.time_Movement_stoppedTimer  = 5
    Data.time_NPCInteraction_lastTime= 5
    Data.time_NPCInteraction_lastTimeSell    = 5
    Data.time_NPCInteraction_lastTimeBuy     = 5
    Data.time_NPCInteraction_lastTimeGive    = 5
    Data.time_Radar_lastTimeClearedList      = 0
    Data.time_Settings_timerDmg      = 5
    Data.time_Settings_timerPots     = 0
    Data.time_Settings_timerDead     = 0
    Data.time_Settings_pickUpTimer   = 5
    Data.time_Skillbot_startUpWaitTime       = 5
    Data.time_Telehack_timerBlock    = 5


# After Phase switch
def _afterLoadPhase(phase,phaseWnd):
    import OpenLib, net, Data
    if phase == OpenLib.PHASE_GAME:
        Data.mainRace = net.GetMainActorRace()
        Data.mainSkillGroup = net.GetMainActorSkillGroup()
        Data.mainVID = net.GetMainActorVID()
        Data.empireID = net.GetEmpireID()
        Data.serverInfo = net.GetServerInfo()
        resetTimers()

Hooks.registerPhaseCallback("DataPhaseCallback",_afterLoadPhase)