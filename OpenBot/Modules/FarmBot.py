from BotBase import BotBase
import Movement
import OpenLib
import UIComponents
import player, ui, chat
 
 
class FarmingBot(BotBase):
 
    def __init__(self):
        BotBase.__init__(self,0.5)
        self.doNotLvlUp = False
        self.is_walking = False  # if False character is using teleport, otherwise character is walking
        self.current_point = 0  # Current position index
        self.path = []  # Dict of tuples with coordinates [(0, 0), (2, 2)] etc
        self.is_waypoint_reached = True
        self.is_turned_on = False
 
        self.Board = ui.BoardWithTitleBar()
        self.Board.SetSize(240, 300)
        self.Board.SetPosition(52, 40)
        self.Board.AddFlag('movable')
        self.Board.SetTitleName('FarmBot')
        self.Board.SetCloseEvent(self.switch_state)
        self.Board.Hide()
 
        comp = UIComponents.Component()
        self.TabWidget = UIComponents.TabWindow(10, 30, 220, 260, self.Board,
                                                ['Moving', 'Mining', 'Metins'])
        self.moving_tab = self.TabWidget.GetTab(0)
        self.minings_tab = self.TabWidget.GetTab(1)
        self.metins_tab = self.TabWidget.GetTab(1)
 
        self.barItems, self.fileListBox, self.ScrollBar = comp.ListBoxEx2(self.moving_tab, 10, 30, 180, 100)
        self.addPointButton = comp.Button(self.moving_tab, 'Add', '', 140, 150, self.add_point,
                                    'd:/ymir work/ui/public/small_Button_01.sub',
                                    'd:/ymir work/ui/public/small_Button_02.sub',
                                    'd:/ymir work/ui/public/small_Button_03.sub')
        self.deletePointButton = comp.Button(self.moving_tab, 'Delete', '', 180, 150, self.remove_selected,
                                    'd:/ymir work/ui/public/small_Button_01.sub',
                                    'd:/ymir work/ui/public/small_Button_02.sub',
                                    'd:/ymir work/ui/public/small_Button_03.sub')
        self.enableButton = comp.OnOffButton(self.moving_tab, '', '', 100, 150,
                                                  OffUpVisual='OpenBot/Images/start_0.tga',
                                                  OffOverVisual='OpenBot/Images/start_1.tga',
                                                  OffDownVisual='OpenBot/Images/start_2.tga',
                                                  OnUpVisual='OpenBot/Images/stop_0.tga',
                                                  OnOverVisual='OpenBot/Images/stop_1.tga',
                                                  OnDownVisual='OpenBot/Images/stop_2.tga',
                                                  funcState=self._start, defaultValue=self.is_turned_on)
 
    def add_point(self):
        (x, y, z) = player.GetMainCharacterPosition()
        self.path.append((round(x), round(y)))
        self.update_points_list()
 
    def remove_selected(self):
        _item = self.fileListBox.GetSelectedItem()
        if _item is None:
            return
        _item_text = _item.GetText().split(',')
        position = (float(_item_text[0]), float(_item_text[1]))
        self.path.remove(position)
        self.update_points_list()
 
    def update_points_list(self):
        self.fileListBox.RemoveAllItems()
        for position in self.path:
            self.fileListBox.AppendItem(OpenLib.Item(str(position[0]) + ', ' + str(position[1]) ))
 
    def next_point(self):
        if self.current_point == len(self.path):
            self.current_point = 0
            reversed(self.path)
        else:
            self.current_point += 1
 
        self.is_waypoint_reached = True
 
    def go_to_next_position(self):
        Movement.GoToPositionAvoidingObjects(self.path[self.current_point][0], self.path[self.current_point][1],
                                             callback=self.next_point)
 
    def _start(self, val):
        if not val:
            chat.AppendChat(3, "[Farming-bot] Canceling moving")
            self.Stop()
        else:
            chat.AppendChat(3, "[Farming-bot] Starting moving")
            self.Start()
 
    def StartBot(self):
        if len(self.path) < 2:
            self._start(False)
            return
 
    def StopBot(self):
        Movement.StopMovement()
 
    def Resume(self):
        self.go_to_next_position()
 
    def Frame(self):
        chat.AppendChat(3, "[Farming-bot] FRAME")
        if self.State == self.STATE_BOTTING and self.is_waypoint_reached:
            self.go_to_next_position()
            self.is_waypoint_reached = False
        elif self.State == self.STATE_BOTTING and not self.is_waypoint_reached:
            chat.AppendChat(3, "[Farming-bot] FRAME MOVING")
 
    def onWaypointReach(self):
        self.is_waypoint_reached = True
 
    def switch_state(self):
        if self.Board.IsShow():
            self.Board.Hide()
        else:
            self.Board.Show()


def switch_state():
    farm.switch_state()
farm = FarmingBot()