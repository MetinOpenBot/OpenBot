from OpenBot.Modules import ChannelSwitcher, Skillbot, OpenLog
from BotBase import BotBase
import DmgHacks
import Movement
import OpenLib, FileManager, Hooks
import UIComponents
import player, ui, chat, chr, net
import eXLib

# STATES
WAITING_STATE = 0
WALKING_STATE = 1
MINING_STATE = 2
FARMING_STATE = 3

def __PhaseTurnOnFarmbot(phase):
    global farm
    if phase == OpenLib.PHASE_GAME:
        if farm.enableButton.isOn:
            farm.Start()

class FarmingBot(BotBase):

    def __init__(self):
        BotBase.__init__(self, 0.1)
        self.CURRENT_STATE = WALKING_STATE
        self.is_walking = True  # if False character is using teleport, otherwise character is walking
        self.current_point = 0  # Current position index
        self.path = []  # Dict of tuples with coordinates [(0, 0), (2, 2)] etc
        self.dont_use_waithack = False
        self.always_use_waithack = False
        self.is_waypoint_reached = False
        self.channel_switching = True
        self.can_change_channel = False

        self.lastTimeMine = 0
        self.lastTimeWaitingState = 0
        self.timeForWaitingState = 5
        self.farm_metins = True
        self.metins_vid_list = []
        self.selectedMetin = 0
        self.farm_ores = False
        self.ores_vid_list = []
        self.ores_to_mine = []
        self.selectedOre = 0


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
                                             funcState=self._start, defaultValue=False)

        self.showWalkButton = comp.OnOffButton(self.moving_tab,
                                              '\t\t\t\t\t\tWalk?',
                                              'If check, character is walking otherwise is teleporting', 125, 140,  funcState=self.switch_walking,
                                              defaultValue=self.is_walking)
        self.showMiningButton = comp.OnOffButton(self.moving_tab,
                                              '\t\t\t\t\t\tMining?',
                                              'Do you want to mine?', 125, 160, funcState=self.switch_mining, defaultValue=self.farm_ores)

        self.showFarmingMetinButton = comp.OnOffButton(self.moving_tab,
                                              '\t\t\t\t\t\tMetins?',
                                              'Do you want farm metins?', 125, 180, funcState=self.switch_farming_metin,
                                                 defaultValue=self.farm_metins)

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

        self.showAlwaysWaithackButton = comp.OnOffButton(self.settings_tab, '\t\t\t\t\t\tAlways use waithack', 'If check, waithack will be turned on even while walking', 20, 80,
                                                         funcState=self.switch_always_use_waithack,
                                                         defaultValue=self.always_use_waithack)

        self.showOffWaithackButton = comp.OnOffButton(self.settings_tab, '\t\t\t\t\t\tDont use waithack', 'If checked, farmbot wont use waithack for destroying metin', 20, 105,
                                                      funcState=self.switch_dont_use_waithack,
                                                      defaultValue=self.dont_use_waithack)

        self.showChannelSwitchingButton = comp.OnOffButton(self.settings_tab, '\t\t\t\t\t\tSwitch channels', 'If checked, farmbot will change to next channel after complete a path', 20, 130,
                                                      funcState=self.switch_channel_switching,
                                                      defaultValue=self.channel_switching)

        self.slot_barWaitingTime, self.edit_lineWaitingTime = \
            comp.EditLine(self.settings_tab, '5', 20, 150, 40, 20, 25)

        self.text_lineWaitingTime = comp.TextLine(self.settings_tab, 's. of waiting after moving', 70, 155, comp.RGB(255, 255, 255))
        self.text_lineWaitingTime1 = comp.TextLine(self.settings_tab, ' or destorying metin',  85, 170, comp.RGB(255, 255, 255))

    def load_path(self):
        path = FileManager.FARMBOT_WAYPOINTS_LISTS + self.edit_line.GetText()
        waypoints = FileManager.LoadListFile(path)
        self.path = []
        for point in waypoints:
            points = point.split(',')
            x = points[0][1:-1]
            y = points[1][1:-1]
            self.path.append((float(x), float(y)))
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

    def switch_always_use_waithack(self, val):
        self.always_use_waithack = val
        if val:
            self.dont_use_waithack = False
            self.showOffWaithackButton.SetOff()

    def switch_channel_switching(self, val):
        self.channel_switching = val

    def switch_dont_use_waithack(self, val):
        self.dont_use_waithack = val

    def switch_walking(self, val):
        self.is_walking = val

    def switch_mining(self, val):
        self.farm_ores = val

    def switch_farming_metin(self, val):
        self.farm_metins = val

    def add_point(self):
        (x, y, z) = player.GetMainCharacterPosition()
        self.path.append((x, y))
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
            self.fileListBox.AppendItem(OpenLib.Item(str(position[0]) + ':' + str(position[1])))

    def next_point(self):
        self.is_waypoint_reached = True
        if self.current_point + 1 >= len(self.path):
            self.path.reverse()
            self.current_point = 1
            if self.channel_switching:
                self.can_change_channel = True
        else:
            self.current_point += 1

    def go_to_next_position(self):
        self.Move(self.path[self.current_point][0], self.path[self.current_point][1], callback=self.onWaypointReach)

    def select_metin(self):
        if(len(self.metins_vid_list) > 0):
            self.selectedMetin = self.metins_vid_list.pop()

    def select_ore(self):
        if(len(self.ores_vid_list) > 0):
            self.selectedOre = self.ores_vid_list.pop()

    def onWaypointReach(self):
        self.next_point()


    def _start(self, val):
        if not val:
            self.Stop()
            DmgHacks.Pause()
        else:
            self.Start()
            

    def StartBot(self):
        if len(self.path) < 2:
            self.Stop()
            DmgHacks.Pause()
            return

    def StopBot(self):
        self.current_point = 0
        Movement.StopMovement()
        self.CURRENT_STATE = WALKING_STATE

    def Move(self, x, y, callback=None):
        if self.is_walking:
            if callback is None:
                Movement.GoToPositionAvoidingObjects(x, y)
            else:
                Movement.GoToPositionAvoidingObjects(x, y, callback=callback)
        else:
            Movement.TeleportToPosition(x, y)
            if callback is not None:
                callback()
            self.lastTimeWaitingState = OpenLib.GetTime()
            self.CURRENT_STATE = WAITING_STATE

    def MoveToVid(self, vid, callback=None):
        chr.SelectInstance(vid)
        x, y, z = chr.GetPixelPosition(vid)
        self.Move(x, y, callback)

    def search_for_farm(self):
        if self.farm_metins and len(self.metins_vid_list) > 0:
            self.select_metin()
            self.CURRENT_STATE = FARMING_STATE
            return FARMING_STATE

        elif self.farm_ores and len(self.ores_vid_list) > 0:
            self.select_ore()
            self.MoveToVid(self.selectedOre)
            self.CURRENT_STATE = MINING_STATE
            return MINING_STATE

        else:
            return WALKING_STATE

    def Frame(self):
        if self.can_change_channel:
            OpenLog.DebugPrint("[Farming-bot] Changing Channel")
            self.can_change_channel = False
            self.go_to_next_channel()
            return

        if self.always_use_waithack:
            DmgHacks.Resume()
        else:
            DmgHacks.Pause()

        self.checkForMetinsAndOres()
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
            if self.search_for_farm() == WALKING_STATE:
                self.go_to_next_position()
                return

        elif self.CURRENT_STATE == MINING_STATE:
            self.mineOre()

            return

        elif self.CURRENT_STATE == FARMING_STATE:
            OpenLog.DebugPrint("[Farming-bot] FARMING_STATE")
            self.farmMetin()

            return

    def mineOre(self):

        # Checking there is any reason to stop mining
        if not self.is_char_ready_to_mine():
            #chat.AppendChat(3, 'Stop')
            return

        val, self.lastTimeMine = OpenLib.timeSleep(self.lastTimeMine, 30)
        if val:
            #chat.AppendChat(3, 'SendOnClickPacket')
            net.SendOnClickPacket(self.selectedOre)

    def farmMetin(self):

        vid_life_status = OpenLib.AttackTarget(self.selectedMetin)

        if vid_life_status == OpenLib.TARGET_IS_DEAD:
            player.SetAttackKeyState(False)
            DmgHacks.Pause()
            self.selectedMetin = 0
            self.lastTimeWaitingState = OpenLib.GetTime()
            self.CURRENT_STATE = WAITING_STATE

        elif vid_life_status == OpenLib.ATTACKING_TARGET:
            if not self.dont_use_waithack:
                DmgHacks.Resume()

        elif vid_life_status == OpenLib.MOVING_TO_TARGET:
            if not self.dont_use_waithack:
                DmgHacks.Resume()

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

    def switch_state(self):
        if self.Board.IsShow():
            self.Board.Hide()
        else:
            self.Board.Show()

    def is_char_ready_to_mine(self):
        if self.selectedOre not in eXLib.InstancesList:
            self.selectedOre = 0
            self.CURRENT_STATE = WALKING_STATE
            return False
        if not OpenLib.isPlayerCloseToInstance(self.selectedOre):
            return False
        return True

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

    def go_to_next_channel(self):
        current_channel = OpenLib.GetCurrentChannel()
        ChannelSwitcher.instance.GetChannels()
        if current_channel + 1 > len(ChannelSwitcher.instance.channels):
            current_channel = 1
        else:
            current_channel += 1

        chat.AppendChat(3, str(current_channel))
        ChannelSwitcher.instance.ChangeChannelById(current_channel)

def switch_state():
    farm.switch_state()


farm = FarmingBot()
Hooks.registerPhaseCallback('farmbotCallback', __PhaseTurnOnFarmbot)
