from OpenBot.Modules.OpenLog import DebugPrint
from OpenBot.Modules.Settings import ItemListDialog
from OpenBot.Modules.Actions import Action, ActionFunctions, ActionRequirementsCheckers, ActionBot
from BotBase import BotBase
import UIComponents, OpenLib
import ui, player, background, chat, item

#
#DT Blacksmith 20074
#DT Weapon Blacksmith 20075
#DT Jewelry Blacksmith 20076
#Demontower 20348
# METIN POS 14080 64335

"""
,


"""

# DUNGEON SCHEMA
DEAMON_TOWER = {
    'requirements': {
        'maps': ['metin2_map_milgyo', 'metin2_map_deviltower1'],
        'lvl': 40,},
    'options': {
        'repeatDungeon': False,
        'endingStage': 6,
        'HowMuchRepeat': 10,
        'CountRepeat': 0,
        'shouldUpgradeItem': False,
        'GoAboveBlacksmith': False,},
    'stages': {
        0: { # stage outside devil tower, entering dt
            'actions': [{ 'function_args': [20348, (53200, 59600), [0, 0], 'metin2_map_milgyo'], # ID, event_answer, posiiton of npc, npc's map
                          'function': ActionFunctions.TalkWithNPC,
                          'requirements': {ActionRequirementsCheckers.IS_IN_MAP: ['metin2_map_deviltower1']},
                          'on_success': [Action.NEXT_ACTION]}]},
        1: { # stage with metin
            'actions': [{'function_args': [(19004, 69011)], # position
                        'function': ActionFunctions.MoveToPosition,
                        'requirements': { ActionRequirementsCheckers.IS_ON_POSITION: (19004, 69011)}
                        },
                        {'function_args': [8015],
                        'function': ActionFunctions.Find,
                        'requirements': {},
                        'on_success': [Action.NEXT_ACTION],
                        'on_failed': []
                        },
                        {'function_args': [8015, 0],
                        'function': ActionFunctions.Destroy,
                        'requirements': {ActionRequirementsCheckers.IS_NEAR_POSITION: (12599, 38399, 1000)},
                        'on_success': [Action.NEXT_ACTION],
                        'on_failed': []
                        }]},
        2: { # stage with only deamons
            'actions': [{ 'function_args': [(15003, 40961)], # ID, event_answer, posiiton of npc, npc's map
                          'function': ActionFunctions.ClearFloor,
                          'requirements': {ActionRequirementsCheckers.IS_NEAR_POSITION: (13400, 14700, 1000)}, #
                          'on_success': [Action.NEXT_ACTION],
                          'on_failed': []
                        }],},
        3: { # stage with king
            'actions': [{ 'function_args': [(17688, 19619)], # ID, event_answer, posiiton of npc, npc's map
                          'function': ActionFunctions.ClearFloor,
                          'requirements': {ActionRequirementsCheckers.IS_NEAR_POSITION: (37037, 62659, 2000)}, # 
                          'on_success': [Action.NEXT_ACTION],
                          'on_failed': []
                        }],},
        4: { # stage with metins
            'actions': [{ 'function_args': [(39123, 65131)], # ID, event_answer, posiiton of npc, npc's map
                          'function': ActionFunctions.ClearFloor,
                          'requirements': {ActionRequirementsCheckers.IS_NEAR_POSITION: (39539, 43607, 5000)}, # IS_NEAR_POSITION: (37722, 63632, 1000)
                          'on_success': [Action.NEXT_ACTION],
                          'on_failed': []
                        }],},
        5: { # stage with keys
            'actions': [{ 'function_args': [(40000, 44000)], # ID, event_answer, posiiton of npc, npc's map
                          'function': ActionFunctions.OpenAllSeals,
                          'requirements': {ActionRequirementsCheckers.IS_NEAR_POSITION: (40713, 19914, 5000)},
                          'on_success': [Action.NEXT_ACTION],
                          'on_failed': []
                        }],},
        6: { # stage with blacksmith
            'actions': [{ 'function_args': [(41000, 20000)],
                          'function': ActionFunctions.ClearFloor,
                          'requirements': {},
                          'on_success': [Action.NEXT_ACTION],
                          'on_failed': []
                        }

                        ],},
        7: { # stage with metins and chests
            'actions': [{ 'function_args': [(61017, 66483)],
                          'function': ActionFunctions.FindMapInDT,
                          'requirements': {ActionRequirementsCheckers.IS_NEAR_POSITION: (60961, 42600, 25000)},
                          'on_success': [Action.NEXT_ACTION],
                          'on_failed': []
                        }
                
            ],},
        8: { # stage with key
            'actions': [
                { 'function_args': [(60961, 42600)],
                          'function': ActionFunctions.OpenASealInMonument,
                          'requirements': {ActionRequirementsCheckers.IS_NEAR_POSITION: (61127, 17160, 25000)},
                          'on_success': [Action.NEXT_ACTION],
                          'on_failed': []
                        }
                        ],},
        9: { # stage with ripper
            'actions': [{ 'function_args': [(61127, 17160)],
                          'function': ActionFunctions.ClearFloor,
                          'requirements': {}, # DONT NEED ANY
                          'on_success': [Action.NEXT_ACTION],
                          'on_failed': []
                        }

                        ],},

    }
}


class AutoDungeon(BotBase):

    def __init__(self):
        BotBase.__init__(self, 0.5)
        self.currSchema = None
        self.currStage = 0
        self.currAction = 0
        self.isCurrActionDone = True
        self.itemFilterList = None
        self.itemToUpgrade = []

        self.options = {
            'UseDmgHack': False,
            'NextChannelIfThereIsAnotherPlayer': False
        }

        self.BuildWindow()

    def BuildWindow(self):
        self.Board = ui.BoardWithTitleBar()
        self.Board.SetSize(235, 235)
        self.Board.SetPosition(52, 40)
        self.Board.AddFlag('movable')
        self.Board.SetTitleName('Auto Dungeon')
        self.Board.SetCloseEvent(self.switch_state)
        self.Board.Hide()

        comp = UIComponents.Component()

        self.TabWidget = UIComponents.TabWindow(10, 30, 215, 195, self.Board, ['DT', 'Settings'])
        
        self.deamon_tower_tab = self.TabWidget.GetTab(0)
        self.settings_tab = self.TabWidget.GetTab(1)

        
        self.shouldUpgradeItemButton = comp.OnOffButton(self.deamon_tower_tab, '\t\t\t\t\t Upgrade item?', 'If u want upgrade item on blacksmith stage, check this', 10, 20,
                                                      funcState=self.switch_should_upgrade_item,
                                                      defaultValue=DEAMON_TOWER['options']['shouldUpgradeItem'])      
        
        self.goAboveBlacksmithButton = comp.OnOffButton(self.deamon_tower_tab, '\t\t\t\t\t\t\t\tGo above blacksmith?', 'Check if u want kill ripper', 10, 50,
                                                      funcState=self.switch_go_above_blacksmith_button,
                                                      defaultValue=DEAMON_TOWER['options']['GoAboveBlacksmith'])
        
        self.barItems, self.fileListBox, self.ScrollBar = comp.ListBoxEx2(self.deamon_tower_tab, 10, 75, 130, 75)
       
        self.openItemFilterButton = comp.Button(self.deamon_tower_tab, 'Open item list', '', 110, 20, self.open_item_filter_dialog,
                                        'd:/ymir work/ui/public/large_Button_01.sub',
                                        'd:/ymir work/ui/public/large_Button_02.sub',
                                        'd:/ymir work/ui/public/large_Button_03.sub')
        
        self.deleteSelectedItemButton = comp.Button(self.deamon_tower_tab, 'Delete', '', 165, 60, self.DeleteItemFilterList,
                                        'd:/ymir work/ui/public/small_Button_01.sub',
                                        'd:/ymir work/ui/public/small_Button_02.sub',
                                        'd:/ymir work/ui/public/small_Button_03.sub')
        
        self.clearListBox = comp.Button(self.deamon_tower_tab, 'Clear', '', 165, 85, self.ClearFilterList,
                                        'd:/ymir work/ui/public/small_Button_01.sub',
                                        'd:/ymir work/ui/public/small_Button_02.sub',
                                        'd:/ymir work/ui/public/small_Button_03.sub')

        self.enableDeamonTower = comp.OnOffButton(self.deamon_tower_tab, '', '', 165, 110,
                                                    OffUpVisual='OpenBot/Images/start_0.tga',
                                                    OffOverVisual='OpenBot/Images/start_1.tga',
                                                    OffDownVisual='OpenBot/Images/start_2.tga',
                                                    OnUpVisual='OpenBot/Images/stop_0.tga',
                                                    OnOverVisual='OpenBot/Images/stop_1.tga',
                                                    OnDownVisual='OpenBot/Images/stop_2.tga',
                                                    funcState=self.switch_launch_auto_dungeon, defaultValue=False)

        self.showRepeatDungeon = comp.OnOffButton(self.settings_tab, '\t\t\t\t\t\tRepeat dungeon', '', 20, 10, funcState=self.switch_next_channel_if_there_is_another_player, defaultValue=self.options['NextChannelIfThereIsAnotherPlayer'])
        self.HowManyRepeatsSlotBar, self.HowManyRepeatsEditLine = comp.EditLine(self.settings_tab, '5', 20, 30, 40, 15, 20)
        self.HowManyRepeatsText = comp.TextLine(self.settings_tab, 'number of repeats', 70, 32, comp.RGB(255, 255, 255))
        self.showNextChannelIfThereIsAnotherPlayerButton = comp.OnOffButton(self.settings_tab, '\t\t\t\t\t\tAvoid players', '', 20, 50, funcState=self.switch_next_channel_if_there_is_another_player, defaultValue=self.options['NextChannelIfThereIsAnotherPlayer'])

    def switch_is_curr_action_done(self):
        if self.isCurrActionDone:
            self.isCurrActionDone = False
        else:
            self.GoToNextAction()
            self.isCurrActionDone = True

    def switch_should_upgrade_item(self, val):
        DEAMON_TOWER['options']['shouldUpgradeItem'] = val
        if val:
            if self.itemFilterList == None:
                self.itemFilterList = ItemListDialog(self.addPickFilterItem, 290, 40)
        else:
            self.itemFilterList = None

    def switch_reapeat_dungeon(self, val):
        DEAMON_TOWER['options']['repeatDungeon'] = val

    def open_item_filter_dialog(self):
        if self.itemFilterList == None:
            self.itemFilterList = ItemListDialog(self.addPickFilterItem, 290, 40)

    def ClearFilterList(self):
        self.itemToUpgrade = []
        self.fileListBox.RemoveAllItems()
        self.UpdateFilterList()

    def UpdateFilterList(self):	
        self.fileListBox.RemoveAllItems()
        for filterItem in sorted(self.itemToUpgrade):
            item.SelectItem(filterItem)
            name = item.GetItemName()
            self.fileListBox.AppendItem(OpenLib.Item(str(filterItem)+" "+name))
                
    def DeleteItemFilterList(self):
        _item = self.fileListBox.GetSelectedItem()
        if _item == None:
            return
        item_name = _item.GetText()
        id = item_name.split(" ",1)
        self.itemToUpgrade.remove(int(id[0]))
        self.UpdateFilterList()
  
    def addPickFilterItem(self,id):
        self.itemToUpgrade.append(int(id))
        self.UpdateFilterList()

    def switch_go_above_blacksmith_button(self, val):
        DEAMON_TOWER['options']['GoAboveBlacksmith'] = val

    def switch_next_channel_if_there_is_another_player(self, val):
        self.options['NextChannelIfThereIsAnotherPlayer'] = val

    def switch_launch_auto_dungeon(self, val):
        if val:
            self.StartDeamonTower()
        else:
            self.Stop()

    def RecognizeStageBot(self):
        if str(background.GetCurrentMapName()) == 'metin2_map_deviltower1':
            if ActionRequirementsCheckers.isNearPosition((15800, 64400, 10000)):
                return 1
            elif ActionRequirementsCheckers.isNearPosition((12599, 38399, 10000)):
                return 2
            elif ActionRequirementsCheckers.isNearPosition((18000, 18000, 10000)):
                return 3
            elif ActionRequirementsCheckers.isNearPosition((37037, 62659, 10000)):
                return 4
            elif ActionRequirementsCheckers.isNearPosition((39539, 43607, 10000)):
                return 5
            elif ActionRequirementsCheckers.isNearPosition((40713, 19914, 10000)):
                return 6
            elif ActionRequirementsCheckers.isNearPosition((61017, 66483, 25000)):
                return 7
            elif ActionRequirementsCheckers.isNearPosition((60961, 42631, 25000)):
                return 8
            elif ActionRequirementsCheckers.isNearPosition((61127, 17162, 25000)):
                return 9
            else:
                DebugPrint('Invalid stage')
                return -1
        else:
             return 0

    def CheckRepeatCount(self):
        count = self.HowManyRepeatsEditLine.GetText()
        if self.is_text_validate(count):
            self.currSchema['options']['HowMuchRepeat'] = int(count)
            return True
        else:
            chat.AppendChat(3, '[AutoDungeon] Invalid repeats number!')
            return False

    def StartDeamonTower(self):
        self.currSchema = DEAMON_TOWER
        if self.currSchema['options']['repeatDungeon']:
            if not self.CheckRepeatCount():
                return
        self.AddOptionalActionsToDeamonTower()
        if self.CheckRequirementsForCurrSchema():
            self.currStage = self.RecognizeStageBot()
            if self.currStage > -1:
                self.Start()
            else:
                self.Stop()
        else:
            self.currSchema = None            

    def AddOptionalActionsToDeamonTower(self):
        slot_to_upgrade = -1
        if self.currSchema['options']['shouldUpgradeItem']:
            for item in self.itemToUpgrade:
                slot = OpenLib.GetItemByID(item)
                if slot > -1:
                    slot_to_upgrade = slot
                    break

        action_dict = {
            'function_args': [self.currSchema['options']['GoAboveBlacksmith'], slot_to_upgrade],
            'function': ActionFunctions.LookForBlacksmithInDeamonTower,
            'requirements':  {},
            'on_failed': [Action.NEXT_ACTION]
        }
        self.currSchema['stages'][6]['actions'].append(action_dict)
        if self.currSchema['options']['repeatDungeon']:
            self.currSchema['options']['endingStage'] = 6
        else:
            self.currSchema['options']['endingStage'] = 9

    def Frame(self):
        if self.isCurrActionDone:
            action_dict = self.currSchema['stages'][self.currStage]['actions'][self.currAction]
            action_dict['callback'] = self.SetIsCurrActionDoneTrue
            self.isCurrActionDone = False
            ActionBot.instance.AddNewAction(action_dict)
            DebugPrint(str(action_dict))

    def switch_state(self):
        if self.Board.IsShow():
            self.Board.Hide()
        else:
            self.Board.Show()

    def is_text_validate(self, text):
        try:
            int(text)
        except ValueError:
            chat.AppendChat(3, '[AutoDungeon] - The value must be a digit')
            return False
        if int(text) < -2:
            chat.AppendChat(3, '[AutoDungeon] - The value must be in range -1 to infinity')
            return False
        return True


def switch_state():
    global instance
    instance.switch_state()

instance = AutoDungeon()