import UIComponents
from BotBase import BotBase
import ui, chat, player, net, m2netm2g
import OpenLib, eXLib, FileManager
import Hooks, Data
from OpenBot.Modules.Actions import ActionBot




def __PhaseChangeSkillCallback(phase,phaseWnd):
    global instance
    if phase == OpenLib.PHASE_GAME:
        instance.resetSkillsUI()
        instance.LoadSettings()
        if instance.shouldWait:
            instance.startUpWait = True
        if instance.enableButton.isOn:
            instance.Start()
        else:
            instance.Stop()


class Skillbot(BotBase):

    ACTIVE_SKILL_IDS = {
        109,
        110,
        111,
        174,
        175,
        19,
        34,
        49,
        63,
        64,
        65,
        78,
        79,
        94,
        95,
        96,
        3,
        4,

    }

    def __init__(self):
        BotBase.__init__(self)
        Data.time_Skillbot_startUpWaitTime = 0
        self.shouldWait = False
        self.startUpWait = False
        self.mode = False
        self.currentSkillSet = []

        self.isOn = False
        self.BuildWindow()
        self.resetSkillsUI()

    def BuildWindow(self):

        self.comp = UIComponents.Component()
        self.Board = ui.BoardWithTitleBar()
        self.Board.SetSize(235, 150)
        self.Board.SetPosition(52, 40)
        self.Board.AddFlag('movable')
        self.Board.SetTitleName('Skillbot')
        self.Board.SetCloseEvent(self.switch_state)
        self.Board.Hide()

        self.enableButton = self.comp.OnOffButton(self.Board, '', '', 15, 40,
                                                  OffUpVisual=eXLib.PATH + 'OpenBot/Images/start_0.tga',
                                                  OffOverVisual=eXLib.PATH + 'OpenBot/Images/start_1.tga',
                                                  OffDownVisual=eXLib.PATH + 'OpenBot/Images/start_2.tga',
                                                  OnUpVisual=eXLib.PATH + 'OpenBot/Images/stop_0.tga',
                                                  OnOverVisual=eXLib.PATH + 'OpenBot/Images/stop_1.tga',
                                                  OnDownVisual=eXLib.PATH + 'OpenBot/Images/stop_2.tga',
                                                  funcState=self._start, defaultValue=self.isOn)
        

        self.showShouldWaitButton = self.comp.OnOffButton(self.Board, '\t\t\t\t\t\tWait after logout?', 'If check, skillbot will wait to use skill', 15, 95,
                                                         funcState=self.switch_should_wait,
                                                         defaultValue=self.shouldWait)

        self.slotBarSlot, self.edit_lineWaitingTime = self.comp.EditLine(self.Board, '5', 15, 117, 25, 15, 25)             
        self.text_line1 = self.comp.TextLine(self.Board, 's. waiting after logout', 50, 118, self.comp.RGB(255, 255, 255))
     
        self.showModeButton = self.comp.OnOffButton(self.Board, '\t\t\t\tCast instant?', 'Not working with every class', 120, 95,
                                                         defaultValue=self.mode)

    def switch_should_wait(self, val):
        self.shouldWait = val

    def SaveSettings(self):
        for skill in self.currentSkillSet:
            FileManager.WriteConfig(str(skill['id']), str(skill['icon'].isOn), file=FileManager.CONFIG_SKILLBOT)
            skillTimer = getattr(self, 'edit_line'+str(skill['id'])).GetText()
            FileManager.WriteConfig('skillTimer'+str(skill['id']), skillTimer, file=FileManager.CONFIG_SKILLBOT)
        FileManager.WriteConfig('IsTurnedOn', str(self.enableButton.isOn), file=FileManager.CONFIG_SKILLBOT)
        FileManager.WriteConfig('ShouldWaitAfterLogout', str(self.shouldWait), file=FileManager.CONFIG_SKILLBOT)
        FileManager.Save(file=FileManager.CONFIG_SKILLBOT)

    def LoadSettings(self):
        is_turned_on = FileManager.boolean(FileManager.ReadConfig('IsTurnedOn', file=FileManager.CONFIG_SKILLBOT))
        if is_turned_on:
            self.enableButton.SetOn()
        else:
            self.enableButton.SetOff()
        
        should_wait = FileManager.boolean(FileManager.ReadConfig('ShouldWaitAfterLogout', file=FileManager.CONFIG_SKILLBOT))
        if should_wait:
            self.showShouldWaitButton.SetOn()
        else:
            self.showShouldWaitButton.SetOff()

        for skill in self.currentSkillSet:
            is_skill_turned_on = FileManager.boolean(FileManager.ReadConfig(str(skill['id']), file=FileManager.CONFIG_SKILLBOT))
            skill_edit_line_timer = getattr(self, 'edit_line'+str(skill['id']))
            skill_edit_line_timer.SetText(FileManager.ReadConfig('skillTimer'+str(skill['id']), file=FileManager.CONFIG_SKILLBOT))
            if is_skill_turned_on:
                if not skill['icon'].isOn:
                    skill['icon'].OnChange()

    def resetSkillsUI(self):
        current_class = OpenLib.GetClass()
        if current_class == OpenLib.SKILL_SET_NONE:
            return
        skillIds = OpenLib.GetClassSkillIDs(current_class)
        del self.currentSkillSet[:]
        self.currentSkillSet = []
        pos_x = 0
        for i, id in enumerate(skillIds):
            if id in self.ACTIVE_SKILL_IDS:
                slot_bar, edit_line = self.comp.EditLine(self.Board, '40', 78 + 35 * pos_x, 75, 25, 15, 25)
                self.currentSkillSet.append({
                    "icon": self.comp.OnOffButton(self.Board, '', '', 75 + 35 * pos_x, 45, image=OpenLib.GetSkillIconPath(id)),
                    "id": id,
                    "slot": i + 1,
                    'is_turned_on': False,
                })
                setattr(self, 'slot_bar'+str(id), slot_bar)
                setattr(self, 'edit_line'+str(id), edit_line)
                pos_x += 1
        self.LoadSettings()

    def _start(self, val):
        if val:
            self.Start()
        else:
            self.Stop()
  
    #def StopBot(self):
    #    self.enableButton.SetOff()

    def addCallbackToWaiter(self, skill):
        def wait_to_use_skill():
            skill['is_turned_on'] = False
        return wait_to_use_skill

    def is_text_validate(self, text):
        try:
            int(text)
        except ValueError:
            chat.AppendChat(3, '[Skillbot] - The value must be a digit')
            return False
        if int(text) < 0:
            chat.AppendChat(3, '[Skillbot] - The value must be in range 0 to infinity')
            return False
        return True

    def Frame(self):

        if not self.startUpWait:
            for skill in self.currentSkillSet:
                if self.showModeButton.isOn:
                    waiter_time = getattr(self, 'edit_line'+str(skill['id'])).GetText()
                    if not self.is_text_validate(waiter_time):
                        continue
                    if not skill['is_turned_on'] and skill['icon'].isOn \
                         and not player.IsSkillCoolTime(skill['slot']):
                        if not player.IsMountingHorse():
                            # chat.AppendChat(3, "[Skill-Bot] Using skill at slot "+str(skill['slot']))
                            
                                eXLib.SendUseSkillPacket(skill['id'], Data.mainVID)
                        else:
                            net.SendCommandPacket(m2netm2g.PLAYER_CMD_RIDE_DOWN)
                            eXLib.SendUseSkillPacket(skill['id'], Data.mainVID)
                            net.SendCommandPacket(m2netm2g.PLAYER_CMD_RIDE)
                        skill['is_turned_on'] = True
                        ActionBot.instance.AddNewWaiter(int(waiter_time), self.addCallbackToWaiter(skill))
                else:
                    if not skill['is_turned_on'] and skill['icon'].isOn \
                        and not player.IsSkillCoolTime(skill['slot']):
                        if not player.IsMountingHorse():
                            eXLib.SendUseSkillPacketBySlot(skill['slot'])
                        else:
                            net.SendCommandPacket(m2netm2g.PLAYER_CMD_RIDE_DOWN)
                            eXLib.SendUseSkillPacketBySlot(skill['slot'])
                            net.SendCommandPacket(m2netm2g.PLAYER_CMD_RIDE)

        else:
            time_to_wait = 2
            text = self.edit_lineWaitingTime.GetText()
            if self.is_text_validate(text):
                time_to_wait = int(text)
            else:
                self.startUpWait = False
                return

            val, Data.time_Skillbot_startUpWaitTime = OpenLib.timeSleep(Data.time_Skillbot_startUpWaitTime, time_to_wait)
            if val:
                self.startUpWait = False


    def switch_state(self):
        if self.Board.IsShow():
            self.SaveSettings()
            self.Board.Hide()
        else:
            self.resetSkillsUI()
            self.Board.Show()


    def __del__(self):
        Hooks.deletePhaseCallback("skillCallback")


def switch_state():
    instance.switch_state()

instance = Skillbot()
Hooks.registerPhaseCallback("skillCallback", __PhaseChangeSkillCallback)
