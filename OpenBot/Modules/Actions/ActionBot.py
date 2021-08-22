from OpenBot.Modules import DmgHacks
import ActionRequirementsCheckers, Action
from OpenBot.Modules.BotBase import BotBase
from OpenBot.Modules.OpenLog import DebugPrint
from OpenBot.Modules import OpenLib, UIComponents
from OpenBot.Modules import Hooks
import ui, chat

# STATES
STATE_CANCELING = -1
STATE_STOP = 0

# STAGES OPTIONS
STAGE_REPEAT = 'stage_reapat'

def _afterLoadPhase(phase):
    global instance
    if phase == OpenLib.PHASE_LOGIN or OpenLib.PHASE_GAME:
        instance.enableActionBot.SetOn()
        instance.Start()
        for waiter in instance.waiters:
            waiter['callback']()
        instance.waiters = []


class ActionBot(BotBase):

    def __init__(self):
        BotBase.__init__(self, 0.2)
        
        self.currState = STATE_STOP

        self.currActionObject = None
        self.currActionsQueue = []

        self.waiters = []


        self.showOffWaithackButton = False
        self.showAlwaysWaithackButton = False
        self.BuildWindow()

    def BuildWindow(self):
        self.comp = UIComponents.Component()
        self.Board = ui.BoardWithTitleBar()
        self.Board.SetSize(235, 275)
        self.Board.SetPosition(52, 40)
        self.Board.AddFlag('movable')
        self.Board.SetTitleName('ActionBot')
        self.Board.SetCloseEvent(self.switch_state)
        self.Board.Hide()

        comp = UIComponents.Component()

        self.TabWidget = UIComponents.TabWindow(10, 30, 215, 235, self.Board, ['General', 'Settings'])

        self.general = self.TabWidget.GetTab(0)
        self.settings_tab = self.TabWidget.GetTab(1)

        self.enableActionBot = comp.OnOffButton(self.general, '', '', 170, 135,
                                                    OffUpVisual='OpenBot/Images/start_0.tga',
                                                    OffOverVisual='OpenBot/Images/start_1.tga',
                                                    OffDownVisual='OpenBot/Images/start_2.tga',
                                                    OnUpVisual='OpenBot/Images/stop_0.tga',
                                                    OnOverVisual='OpenBot/Images/stop_1.tga',
                                                    OnDownVisual='OpenBot/Images/stop_2.tga',
                                                    funcState=self.OnEnableSwitchButton, defaultValue=False)
        
        self.ClearButton = comp.Button(self.general, 'Clear', '', 20, 135, self.OnClearButton,
                                          'd:/ymir work/ui/public/large_Button_01.sub',
                                          'd:/ymir work/ui/public/large_Button_02.sub',
                                          'd:/ymir work/ui/public/large_Button_03.sub')
        self.ShowButton = comp.Button(self.general, 'Show', '', 20, 155, self.OnClearButton,
                                          'd:/ymir work/ui/public/large_Button_01.sub',
                                          'd:/ymir work/ui/public/large_Button_02.sub',
                                          'd:/ymir work/ui/public/large_Button_03.sub')


    def OnEnableSwitchButton(self, val):
        if val:
            self.Start()
        else:
            self.Stop()
            
    def OnClearButton(self):

        if self.currActionObject is not None:
            self.currActionObject.CallCallback()

        for action in self.currActionsQueue:
            action.CallCallback()

        for waiter in self.waiters:
            waiter['callback']()
        
        self.currActionObject = None
        self.currActionsQueue = []
        self.waiters = []

    def GetNewId(self):
        return 0

    def GoToNextAction(self):
        if self.currActionObject.callback is not None:
            DebugPrint('Calling callback')
            self.currActionObject.CallCallback()

        if self.currActionsQueue:
            self.currActionObject = self.currActionsQueue.pop()
        else:
            self.currActionObject = None

    def ConvertDictActionToObjectAction(self, action_dict):
        action_dict_keys = action_dict.keys()
        if 'function' not in action_dict_keys and 'function_args' not in action_dict_keys:
            DebugPrint('Action dict dont have function or function_args!')
            return
        new_action = Action.Action(id=self.GetNewId,
                            function=action_dict['function'])

        for key in action_dict_keys:
            if key is not 'function':
                setattr(new_action, key, action_dict[key])
        
        return new_action
        
    def NewActionReturned(self, action):
        if not self.currActionObject in self.currActionsQueue:
            self.currActionsQueue.append(self.currActionObject)

        if isinstance(action, Action.Action):
            self.currActionObject = action
        else:
            new_action = self.ConvertDictActionToObjectAction(action)
            self.currActionObject = new_action

    def AddNewAction(self, action):
        if type(action) == Action.Action:
            self.currActionsQueue.append(action)
        else:
            new_action = self.ConvertDictActionToObjectAction(action)
            DebugPrint('Converted Dict action to object action')
            self.currActionsQueue.append(new_action)          

    def CheckIsThereNewAction(self):
        if not len(self.currActionsQueue):
            return False
        else:
            self.currActionObject = self.currActionsQueue.pop()
            return True

    def StopBot(self):
        self.OnClearButton()

    def Frame(self):
        self.rendered_actions = []
        self.rendered_waiters = []
        names = ['Going to enemy']

        if self.Board.IsShow():
            self.RefreshRenderedWaiters()

        for waiter in self.waiters:
            this_time = OpenLib.GetTime()
            if this_time > waiter['timeToWait'] + waiter['launching_time']:
                waiter['callback']()
                self.waiters.remove(waiter)

        if self.currActionObject == None:
            if not self.CheckIsThereNewAction():
                return

        if not self.showOffWaithackButton:
            if self.showAlwaysWaithackButton:
                DmgHacks.Resume()
            else:
                if self.currActionObject.function.__name__ in ['Destroy', 'ClearFloor', 'LookForBlacksmithInDeamonTower',
                                                               'FindMapInDT', 'OpenASealInMonument'] or \
                    self.currActionObject.name in names:
                    DmgHacks.Resume()
                else:
                    DmgHacks.Pause()
        else:
            DmgHacks.Pause()
        
        self.FrameDoAction()

    def AddNewWaiter(self, timeToWait, callback):
        self.waiters.append({
            'timeToWait': timeToWait,
            'callback': callback,
            'launching_time': OpenLib.GetTime(),
        })     

    def FrameDoAction(self):
        if self.Board.IsShow():
            self.RefreshRenderedActions()

        action_result = self.currActionObject.CallFunction()

        if type(action_result) == str:
            
            if action_result == Action.NEXT_ACTION:
                self.GoToNextAction()
                DebugPrint('Action do NEXT_ACTION')

            elif action_result == Action.DISCARD_PREVIOUS:
                self.GoToNextAction()
                self.GoToNextAction()
                DebugPrint('Action do DISCARD_PREVIOUS')
            
            elif action_result == Action.REQUIREMENTS_NOT_DONE:
                DebugPrint('Action do REQUIREMENTS_NOT_DONE')

            elif action_result == Action.NOTHING:
                DebugPrint('Action do nothing')
                
            elif action_result == Action.ERROR:
                DebugPrint('Action has some error')
                #self.GoToNextAction()
        
        elif isinstance(action_result, Action.Action) or type(action_result) == dict:
            DebugPrint('New action returned')
            self.NewActionReturned(action_result)



    def RefreshRenderedActions(self):
        actions_to_render = [self.currActionObject] + self.currActionsQueue
        self.rendered_actions = []
        x = 10
        y = 15
        comp = UIComponents.Component()
        for action in actions_to_render:
            self.rendered_actions.append(comp.TextLine(self.general, action.name, x, y, UIComponents.RGB(255, 255, 255)))
            y += 20
    
    def RefreshRenderedWaiters(self):
        x = 100
        y = 15
        self.rendered_waiters = []
        comp = UIComponents.Component()
        for action in self.waiters:
            self.rendered_waiters.append(comp.TextLine(self.general, action['callback'].__name__, x, y, UIComponents.RGB(255, 255, 255)))
            y += 20

    def switch_state(self):
        if self.Board.IsShow():
            self.Board.Hide()
        else:
            self.Board.Show()

instance = ActionBot()
Hooks.registerPhaseCallback('actionBot', _afterLoadPhase)
