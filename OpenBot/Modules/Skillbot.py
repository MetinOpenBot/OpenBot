import UIComponents
from BotBase import BotBase
import ui, chat, player, net, m2netm2g
import OpenLib, eXLib, FileManager
import Hooks




def __PhaseChangeSkillCallback(phase):
    global instance
    if phase == OpenLib.PHASE_GAME:
        instance.resetSkillsUI()
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
        self.startUpWaitTime = 0
        self.startUpWait = False
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
                                                  OffUpVisual='OpenBot/Images/start_0.tga',
                                                  OffOverVisual='OpenBot/Images/start_1.tga',
                                                  OffDownVisual='OpenBot/Images/start_2.tga',
                                                  OnUpVisual='OpenBot/Images/stop_0.tga',
                                                  OnOverVisual='OpenBot/Images/stop_1.tga',
                                                  OnDownVisual='OpenBot/Images/stop_2.tga',
                                                  funcState=self._start, defaultValue=self.isOn)


    def SaveSettings(self):
        for skill in self.currentSkillSet:
            FileManager.WriteConfig(str(skill['id']), str(skill['icon'].isOn), file=FileManager.CONFIG_SKILLBOT)
        FileManager.WriteConfig('IsTurnedOn', str(self.isOn), file=FileManager.CONFIG_SKILLBOT)
        FileManager.Save(file=FileManager.CONFIG_SKILLBOT)

    def LoadSettings(self):
        is_turned_on = FileManager.boolean(FileManager.ReadConfig('IsTurnedOn', file=FileManager.CONFIG_SKILLBOT))
        if is_turned_on:
            self.enableButton.SetOn()
        else:
            self.enableButton.SetOff()
        
        for skill in self.currentSkillSet:
            is_skill_turned_on = FileManager.boolean(FileManager.ReadConfig(str(skill['id']), file=FileManager.CONFIG_SKILLBOT))
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
                self.currentSkillSet.append({
                    "icon": self.comp.OnOffButton(self.Board, '', '', 15 + 35 * pos_x, 100, image=OpenLib.GetSkillIconPath(id)),
                    "id": id,
                    "slot": i + 1,
                })
                pos_x += 1
        self.LoadSettings()

    def _start(self, val):
        if val:
            self.Start()
        else:
            self.Stop()


    def Frame(self):
        if not self.startUpWait:
            for skill in self.currentSkillSet:
                if not player.IsSkillCoolTime(skill['slot']) and skill['icon'].isOn:
                    if not player.IsMountingHorse():
                        # chat.AppendChat(3, "[Skill-Bot] Using skill at slot "+str(skill['slot']))
                        eXLib.SendUseSkillPacketBySlot(skill['slot'], net.GetMainActorVID())
                    else:
                        net.SendCommandPacket(m2netm2g.PLAYER_CMD_RIDE_DOWN)
                        eXLib.SendUseSkillPacketBySlot(skill['slot'], net.GetMainActorVID())
                        net.SendCommandPacket(m2netm2g.PLAYER_CMD_RIDE)
        else:
            val, self.startUpWaitTime = OpenLib.timeSleep(self.startUpWaitTime, 2)
            if val:
                self.startUpWait = False


    def switch_state(self):
        if self.Board.IsShow():
            self.SaveSettings()
            self.Board.Hide()
        else:
            self.Board.Show()


    def __del__(self):
        Hooks.deletePhaseCallback("skillCallback")


def switch_state():
    instance.switch_state()

instance = Skillbot()
Hooks.registerPhaseCallback("skillCallback", __PhaseChangeSkillCallback)