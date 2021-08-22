from OpenBot.Modules.Actions import Action, ActionBot, ActionFunctions, ActionRequirementsCheckers
from OpenBot.Modules import ChannelSwitcher, OpenLog
from BotBase import BotBase
import DmgHacks
import Movement
import OpenLib, FileManager, Hooks
import UIComponents
import player, ui, chat, chr, net, background
import eXLib

# STATES
WAITING_STATE = 0
WALKING_STATE = 1
MINING_STATE = 2
FARMING_STATE = 3
EXCHANGING_ITEMS_TO_ENERGY = 4

def __PhaseTurnOnFarmbot(phase):
    global farm
    if phase == OpenLib.PHASE_GAME:
        if farm.enableButton.isOn:
            farm.Start()

def OnDigMotionCallback(main_vid,target_ore,n):
    global farm
    if(main_vid != net.GetMainActorVID()):
        return
    if farm.enableButton.isOn and farm.showMiningButton.isOn:
        OpenLog.DebugPrint('Digging is starting')
        farm.is_currently_digging = True
        slash_time = n * farm.MINING_SLASH_TIME
        ActionBot.instance.AddNewWaiter(slash_time, farm.IsCurrentlyDiggingDone)

def returnFuncWithArgs(func, args):

    def x():
        func(args)
    
    return x

class FarmingBot(BotBase):

    MINING_SLASH_TIME = 2.1

    def __init__(self):
        BotBase.__init__(self, 0.1,waitIsPlayerDead=True)
        self.CURRENT_STATE = WALKING_STATE
        self.current_point = 0  # Current position index
        self.path = []  # Dict of tuples with coordinates [(0, 0), (2, 2)] etc
        eXLib.RegisterDigMotionCallback(OnDigMotionCallback)
        
        self.slash_timer = OpenLib.GetTime()
        self.hasRecivedSlash = False
        self.lastTimeMine = 0   
        self.ores_vid_list = []
        self.ores_to_mine = []
        self.selectedOre = 0
        self.is_currently_digging = False

        self.metins_vid_list = []
        self.selectedMetin = 0

        self.lastTimeWaitingState = 0
        self.timeForWaitingState = 5

        self.isReadyToSwitchChannel = False
        self.BuildWindow()

    def BuildWindow(self):
        self.Board = ui.BoardWithTitleBar()
        self.Board.SetSize(240, 300)
        self.Board.SetPosition(52, 40)
        self.Board.AddFlag('movable')
        self.Board.SetTitleName('FarmBot')
        self.Board.SetCloseEvent(self.switch_state)
        self.Board.Hide()

        comp = UIComponents.Component()
        self.TabWidget = UIComponents.TabWindow(10, 30, 220, 260, self.Board,
                                                ['Moving', 'Mining', 'Settings'])
        self.moving_tab = self.TabWidget.GetTab(0)
        self.minings_tab = self.TabWidget.GetTab(1)
        self.settings_tab = self.TabWidget.GetTab(2)

        # Moving tab
        self.barItems, self.fileListBox, self.ScrollBar = comp.ListBoxEx2(self.moving_tab, 10, 30, 180, 100)
        self.addPointButton = comp.Button(self.moving_tab, 'Add', 'Add current position to path', 10, 140, self.add_point,
                                          'd:/ymir work/ui/public/small_Button_01.sub',
                                          'd:/ymir work/ui/public/small_Button_02.sub',
                                          'd:/ymir work/ui/public/small_Button_03.sub')
        self.deletePointButton = comp.Button(self.moving_tab, 'Delete', 'Delete selected position in path', 10, 165, self.remove_selected,
                                             'd:/ymir work/ui/public/small_Button_01.sub',
                                             'd:/ymir work/ui/public/small_Button_02.sub',
                                             'd:/ymir work/ui/public/small_Button_03.sub')
        self.deleteAllPointsButton = comp.Button(self.moving_tab, 'Clear', 'Clear path', 10, 190, self.remove_all,
                                             'd:/ymir work/ui/public/small_Button_01.sub',
                                             'd:/ymir work/ui/public/small_Button_02.sub',
                                             'd:/ymir work/ui/public/small_Button_03.sub')

        self.enableButton = comp.OnOffButton(self.moving_tab, '', 'Start', 70, 140,
                                             OffUpVisual='OpenBot/Images/start_0.tga',
                                             OffOverVisual='OpenBot/Images/start_1.tga',
                                             OffDownVisual='OpenBot/Images/start_2.tga',
                                             OnUpVisual='OpenBot/Images/stop_0.tga',
                                             OnOverVisual='OpenBot/Images/stop_1.tga',
                                             OnDownVisual='OpenBot/Images/stop_2.tga',
                                             funcState=self.OnEnableSwitchButton, defaultValue=False)

        self.showMiningButton = comp.OnOffButton(self.moving_tab, '\t\t\t\t\t\tMining?',
        'Do you want to mine?', 125, 140, funcState=self.ButtonOnOff, defaultValue=False)

        self.showFarmingMetinButton = comp.OnOffButton(self.moving_tab, '\t\t\t\t\t\tMetins?',
        'Do you want farm metins?', 125, 160, funcState=self.ButtonOnOff, defaultValue=False)

        # Ores tab
        index_y = 0
        index_x = 0
        for ore in OpenLib.ORES_IDS:
            setattr(self, 'is_mine_' + str(ore), False)
            button = comp.OnOffButton(self.minings_tab,
                             '',
                             '', 30+(index_x*60), 30+(index_y*40),image="icon/item/"+OpenLib.ORES_IDS[ore]+".tga", funcState=self.create_switch_function('is_mine_' + str(ore), ore),
                             defaultValue=getattr(self, 'is_mine_' + str(ore)))
            setattr(self, str(ore)+'Button', button)

            index_y += 1
            if index_y % 4 == 0:
                index_y = 0
                index_x += 1

        # Settings tab
        self.settingsLoadButton =   comp.Button(self.settings_tab, 'Load', 'Load path by name of file', 20, 30, self.load_path,
                                             'd:/ymir work/ui/public/small_Button_01.sub',
                                             'd:/ymir work/ui/public/small_Button_02.sub',
                                             'd:/ymir work/ui/public/small_Button_03.sub')

        self.text_lineEditLine = comp.TextLine(self.settings_tab, 'name of file to load/save', 75, 20, comp.RGB(255, 255, 255))
        self.slot_bar, self.edit_line = comp.EditLine(self.settings_tab, 'filename.txt', 70, 40, 120, 25, 25)

        self.settingsSaveButton =   comp.Button(self.settings_tab, 'Save', 'Save path by name of file', 20, 55, self.save_path,
                                             'd:/ymir work/ui/public/small_Button_01.sub',
                                             'd:/ymir work/ui/public/small_Button_02.sub',
                                             'd:/ymir work/ui/public/small_Button_03.sub')



        self.showChannelSwitchingButton = comp.OnOffButton(self.settings_tab, '\t\t\t\t\tSwitch channels',
         'If checked, farmbot will change to next channel after complete a path', 20, 80,
                                                      funcState=self.ButtonOnOff,
                                                      defaultValue=False)

                
        self.showAlwaysWaithackButton = comp.OnOffButton(self.settings_tab, '\t\t\t\t\t\t\tAlways use waithack', 'If check, waithack will be turned on even while walking', 20, 100,
                                                         funcState=self.switch_always_use_waithack,
                                                         defaultValue=ActionBot.instance.showAlwaysWaithackButton)

        self.showOffWaithackButton = comp.OnOffButton(self.settings_tab, '\t\t\t\t\t\tDont use waithack', 'If checked, farmbot wont use waithack for destroying metin', 20, 120,
                                                      funcState=self.switch_dont_use_waithack,
                                                      defaultValue=ActionBot.instance.showOffWaithackButton)

        self.showExchangeTrash = comp.OnOffButton(self.settings_tab, '\t\t\t\t\t\t\t\t\t\t\t\tExchange to energy fragments', 'This option allow farmbot to exchange items listed in settings > shop to energy fragments.', 20, 140,
                                                funcState=self.ButtonOnOff,
                                                defaultValue=False)                                                 

        self.slot_barWaitingTime, self.edit_lineWaitingTime = \
            comp.EditLine(self.settings_tab, '5', 20, 170, 40, 20, 25)

        self.text_lineWaitingTime = comp.TextLine(self.settings_tab, 's. of waiting after ', 70, 175, comp.RGB(255, 255, 255))
        self.text_lineWaitingTime1 = comp.TextLine(self.settings_tab, 'destorying metin',  75, 185, comp.RGB(255, 255, 255))


    def switch_always_use_waithack(self, val):
        ActionBot.instance.showAlwaysWaithackButton = val

    def switch_dont_use_waithack(self, val):
        ActionBot.instance.showOffWaithackButton = val


    def OnEnableSwitchButton(self, val):
        if val:
            self.Start()
        else:
            self.Stop()

    def ButtonOnOff(self, val):
        pass

    def IsWalkingDone(self):
        self.isCurrActionDone = True
        self.CURRENT_STATE = WALKING_STATE
        self.next_point()

    def IsDestroyingMetinDone(self):
        self.isCurrActionDone = True
        self.selectedMetin = 0
        self.CURRENT_STATE = WAITING_STATE
        self.lastTimeWaitingState = OpenLib.GetTime()

    def IsCurrentlyDiggingDone(self):
        self.is_currently_digging = False
        self.isCurrActionDone = True

    def IsExchangingItemsToEnergyFragmentsDone(self):
        self.isCurrActionDone = True
        self.CURRENT_STATE = WALKING_STATE

    def IsCurrentlyDigging(self):
        return self.is_currently_digging

    def load_path(self):
        path = FileManager.FARMBOT_WAYPOINTS_LISTS + self.edit_line.GetText()
        waypoints = FileManager.LoadListFile(path)
        self.path = []
        for point in waypoints:
            points = point.split(',')
            x = points[0][1:-1]
            y = points[1][1:-1]
            name = points[2][2:-2]
            OpenLog.DebugPrint(str(points))
            self.path.append((float(x), float(y), str(name)))
        self.update_points_list()

    def save_path(self):
        path = FileManager.FARMBOT_WAYPOINTS_LISTS + self.edit_line.GetText()
        FileManager.SaveListFile(path, self.path)

    def remove_all(self):
        self.fileListBox.RemoveAllItems()
        self.path = []

    def create_switch_function(self, arg_name, ore_id):

        def function(val):
            setattr(self, arg_name, val)
            if val:
                self.ores_to_mine.append(ore_id)
            else:
                if ore_id in self.ores_to_mine:
                    self.ores_to_mine.remove(ore_id)

        return function

    def add_point(self):
        x, y, z = player.GetMainCharacterPosition()
        self.path.append((x, y, background.GetCurrentMapName()))
        self.update_points_list()

    def remove_selected(self):
        _item = self.fileListBox.GetSelectedItem()
        if _item is None:
            return
        _item_text = _item.GetText().split(':')
        position = (float(_item_text[0]), float(_item_text[1]))
        self.path.remove(position)
        self.update_points_list()

    def update_points_list(self):
        self.fileListBox.RemoveAllItems()
        for position in self.path:
            x, y = int(position[0]), int(position[1])
            self.fileListBox.AppendItem(OpenLib.Item(str(x) + ':' + str(y) + ':' + position[2]))

    def next_point(self):
        if self.current_point + 1 < len(self.path):
            self.current_point += 1
        else:
            self.path.reverse()
            self.current_point = 0
            if self.showChannelSwitchingButton.isOn:
                self.isReadyToSwitchChannel = True

    def select_metin(self):
        if self.metins_vid_list:
            self.selectedMetin = self.metins_vid_list.pop()

    def select_ore(self):
        if self.ores_vid_list:
            self.selectedOre = self.ores_vid_list.pop()

    def StartBot(self):
        if len(self.path) < 2:
            self.Stop()
            DmgHacks.Pause()
            self.enableButton.SetOff()
            return

    def StopBot(self):
        self.current_point = 0
        Movement.StopMovement()
        self.CURRENT_STATE = WALKING_STATE

    def search_for_farm(self):
        if self.showFarmingMetinButton.isOn and len(self.metins_vid_list) > 0:
            self.select_metin()
            self.CURRENT_STATE = FARMING_STATE

        elif self.showMiningButton.isOn and len(self.ores_vid_list) > 0:
            self.select_ore()
            self.CURRENT_STATE = MINING_STATE
            return
        else:
            if not self.lastTimeWaitingState and not self.CURRENT_STATE == EXCHANGING_ITEMS_TO_ENERGY:
                self.CURRENT_STATE = WALKING_STATE


    def Pause(self):
        DmgHacks.Pause()
    
    def Resume(self):
        pass

    def CanPause(self):
        return True

    def go_to_next_channel(self):
        action_dict = {
            'function_args': [OpenLib.GetNextChannel()],
            'function': ActionFunctions.ChangeChannel,
            'requirements': {ActionRequirementsCheckers.IS_IN_CHANNEL: [OpenLib.GetNextChannel()]},
            'on_success': [Action.NEXT_ACTION],
            'callback': self.SetIsCurrActionDoneTrue,
        }
        ActionBot.instance.AddNewAction(action_dict)

    def is_text_validate(self, text):
        try:
            int(text)
        except ValueError:
            chat.AppendChat(3, '[Farmbot] - The value must be a digit')
            return False
        if int(text) < 0:
            chat.AppendChat(3, '[Farmbot] - The value must be in range 0 to infinity')
            return False
        return True

    def switch_state(self):
        if self.Board.IsShow():
            self.Board.Hide()
        else:
            self.Board.Show()

    def checkForMetinsAndOres(self):
        self.ores_vid_list = []
        self.metins_vid_list = []
        for vid in eXLib.InstancesList:
            if OpenLib.IsThisOre(vid):
                chr.SelectInstance(vid)
                if chr.GetRace() in self.ores_to_mine:
                    self.ores_vid_list.append(vid)
            elif OpenLib.IsThisMetin(vid) and not eXLib.IsDead(vid):
                self.metins_vid_list.append(vid)

    def Frame(self):

        if self.isCurrActionDone:
            self.checkForMetinsAndOres()
            self.search_for_farm()

            if self.isReadyToSwitchChannel:
                self.isReadyToSwitchChannel = False
                self.isCurrActionDone = False
                self.go_to_next_channel()
                return

            if self.CURRENT_STATE == WAITING_STATE:

                OpenLog.DebugPrint("[Farming-bot] WAITING_STATE")
                text = self.edit_lineWaitingTime.GetText()
                if self.is_text_validate(text):
                    self.timeForWaitingState = int(text)
                val, self.lastTimeWaitingState = OpenLib.timeSleep(self.lastTimeWaitingState, self.timeForWaitingState)
                if val:
                    self.lastTimeWaitingState = 0
                    self.CURRENT_STATE = WALKING_STATE
                else:
                    self.search_for_farm()

            if self.CURRENT_STATE == WALKING_STATE:
                OpenLog.DebugPrint("[Farming-bot] WALKING_STATE")
                
                if OpenLib.isInventoryFull():
                    from OpenBot.Modules import Settings
                    if self.showExchangeTrash.isOn:
                        for item in Settings.instance.sellItems:
                            slot=OpenLib.GetItemByID(item)
                            if slot > -1:
                                OpenLog.DebugPrint('changing state to exchaning items')
                                self.CURRENT_STATE = EXCHANGING_ITEMS_TO_ENERGY
                                return
                else:
                    OpenLog.DebugPrint('inventory is not full')
                OpenLog.DebugPrint('No trash items')

                interruptors_args = []
                interruptors = []

                if self.showFarmingMetinButton.isOn:
                    interruptors_args.append(0)
                    interruptors.append(ActionRequirementsCheckers.isMetinNearly)

                if self.showMiningButton.isOn:
                    interruptors_args.append(self.ores_to_mine)
                    interruptors.append(ActionRequirementsCheckers.isRaceNearly)

                if interruptors:
                    interrupt_function = lambda: Action.NEXT_ACTION
                else:
                    interrupt_function = None

                action_dict = {
                'function_args': [(self.path[self.current_point][0], self.path[self.current_point][1]), self.path[self.current_point][2]],
                'function': ActionFunctions.MoveToPosition, 
                'requirements': {ActionRequirementsCheckers.IS_ON_POSITION: [self.path[self.current_point][0],
                                                                            self.path[self.current_point][1], 200],
                                                                             ActionRequirementsCheckers.IS_IN_MAP: [self.path[self.current_point][2]]},
                'callback': self.IsWalkingDone,
                'interruptors_args': interruptors_args,
                'interruptors': interruptors,
                'interrupt_function': interrupt_function}
                ActionBot.instance.AddNewAction(action_dict)
                self.isCurrActionDone = False
                return

            elif self.CURRENT_STATE == MINING_STATE:
                OpenLog.DebugPrint("[Farming-bot] MINING_STATE")
                action_dict = {
                    'function_args': [self.selectedOre, self.IsCurrentlyDigging],
                    'requirements': {},
                    'function': ActionFunctions.MineOre,
                    'on_success': [Action.NEXT_ACTION],
                    'on_failed': [Action.NEXT_ACTION]
                }

                ActionBot.instance.AddNewAction(action_dict)
                self.isCurrActionDone = False
                return

            elif self.CURRENT_STATE == FARMING_STATE:
                OpenLog.DebugPrint("[Farming-bot] FARMING_STATE")
                action_dict = {'function_args': [0, self.selectedMetin],
                            'function': ActionFunctions.Destroy,
                            'requirements': {},
                            'on_success': [Action.NEXT_ACTION],
                            'on_failed': [],
                            'callback': self.IsDestroyingMetinDone
                            }
                ActionBot.instance.AddNewAction(action_dict)
                self.isCurrActionDone = False
                return
            
            elif self.CURRENT_STATE == EXCHANGING_ITEMS_TO_ENERGY:
                OpenLog.DebugPrint('[Farming-bot] EXCHANGING_STATE')
                action_dict = {'function_args': [],
                                'function': ActionFunctions.ExchangeTrashItemsToEnergyFragments,
                                'on_success': [Action.NEXT_ACTION],
                                'callback': self.IsExchangingItemsToEnergyFragmentsDone}
                ActionBot.instance.AddNewAction(action_dict)
                self.isCurrActionDone = False
                return



def switch_state():
    global farm
    farm.switch_state()


farm = FarmingBot()
Hooks.registerPhaseCallback('farmbotCallback', __PhaseTurnOnFarmbot)