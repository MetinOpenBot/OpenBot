from OpenBot.Modules.Actions import ActionBot
from OpenBot.Modules import EnergyBot
import ui,app,chat,chr,net,player,wndMgr,uiCommon,eXLib
from OpenBot.Modules import FileManager, UIComponents, ShopSearcher,Telehack, PythonManager, Settings, Levelbot, Spambot, Shopcreator, Inventorymanager, FishingBot, KeyBot
from OpenBot.Modules import FarmingBot
from OpenBot.Modules import Radar, Skillbot, ChannelSwitcher, AutoDungeon
from OpenBot.Modules.Radar import Radar
from OpenBot.Modules.Actions import ActionBot

DEBUG = False
if DEBUG:
    from OpenBot.Modules import Filter, MiningBot

class OpenBotHackbarDialog(ui.ScriptWindow): 				

    Hackbar = 0
    Teleport = 0
    ShortCuts = 0

    comp = UIComponents.Component()
    #buff = Buffbot.BuffDialog()
    spam = Spambot.SpamDialog()
    action_bot = ActionBot.instance
    energy_bot = EnergyBot.instance
    radar = Radar()
    tele = Telehack.TeleportHackDialog()
    python_manager = PythonManager.PythonManagerDialog()


    def __init__(self):
        self.OpenBotBoard = ui.ThinBoard(layer="TOP_MOST")
        self.OpenBotBoard.SetPosition(0, 40)
        if DEBUG:
            self.OpenBotBoard.SetSize(51, 500)
        else:
            self.OpenBotBoard.SetSize(51, 550)
        self.OpenBotBoard.AddFlag("float")
        self.OpenBotBoard.AddFlag("movable")
        self.OpenBotBoard.Hide()
        if DEBUG:
            self.filter = Filter.FilterDialog()

        self.ShowHackbarButton = self.comp.Button(None, '', 'Show Hackbar', wndMgr.GetScreenWidth()-99, 260, self.OpenHackbar, eXLib.PATH + 'OpenBot/Images/Shortcuts/show_0.tga', eXLib.PATH + 'OpenBot/Images/Shortcuts/show_1.tga', eXLib.PATH + 'OpenBot/Images/Shortcuts/show_0.tga')
        self.HideHackbarButton = self.comp.HideButton(None, '', 'Hide Hackbar', wndMgr.GetScreenWidth()-99, 260, self.OpenHackbar, eXLib.PATH + 'OpenBot/Images/Shortcuts/hide_0.tga', eXLib.PATH + 'OpenBot/Images/Shortcuts/hide_1.tga', eXLib.PATH + 'OpenBot/Images/Shortcuts/hide_0.tga')
        self.ShortCutButton = self.comp.Button(None, '', 'ShortCuts', wndMgr.GetScreenWidth()-62, 260, self.OpenShortCuts, eXLib.PATH + 'OpenBot/Images/Shortcuts/shortcut_0.tga', eXLib.PATH + 'OpenBot/Images/Shortcuts/shortcut_1.tga', eXLib.PATH + 'OpenBot/Images/Shortcuts/shortcut_0.tga')

        self.GhostButton = self.comp.HideButton(None, '', 'Ghostmode', wndMgr.GetScreenWidth()-115, 310, self.GhostMod, eXLib.PATH + 'OpenBot/Images/Shortcuts/ghost_0.tga', eXLib.PATH + 'OpenBot/Images/Shortcuts/ghost_1.tga', eXLib.PATH + 'OpenBot/Images/Shortcuts/ghost_0.tga')
        self.TeleportButton = self.comp.HideButton(None, '', 'Teleporthack', wndMgr.GetScreenWidth()-80, 310, self.OpenTeleport, eXLib.PATH + 'OpenBot/Images/Shortcuts/tele_0.tga', eXLib.PATH + 'OpenBot/Images/Shortcuts/tele_1.tga', eXLib.PATH + 'OpenBot/Images/Shortcuts/tele_0.tga')
        self.CrashButton = self.comp.HideButton(None, '', 'Exit', wndMgr.GetScreenWidth()-45, 310, self.CloseRequest, eXLib.PATH + 'OpenBot/Images/Shortcuts/close_0.tga', eXLib.PATH + 'OpenBot/Images/Shortcuts/close_1.tga', eXLib.PATH + 'OpenBot/Images/Shortcuts/close_0.tga')
        self.ZoomButton = self.comp.HideButton(None, '', 'Zoom-Hack', wndMgr.GetScreenWidth()-115, 350, self.Zoom, eXLib.PATH + 'OpenBot/Images/Shortcuts/zoom_0.tga', eXLib.PATH + 'OpenBot/Images/Shortcuts/zoom_1.tga', eXLib.PATH + 'OpenBot/Images/Shortcuts/zoom_0.tga')
        self.NoFogButton = self.comp.HideButton(None, '', 'No-Fog', wndMgr.GetScreenWidth()-80, 350, self.NoFog, eXLib.PATH + 'OpenBot/Images/General/nofog_0.tga', eXLib.PATH + 'OpenBot/Images/General/nofog_1.tga', eXLib.PATH + 'OpenBot/Images/General/nofog_0.tga')



        self.SpamtextCombo = self.comp.ComboBox(None, 'Text 1', wndMgr.GetScreenWidth()-70, 490, 55)
        SpamList = ("Text 1", "Text 2", "Text 3", "Text 4", "Text 5", "Text 6", "Text 7", "Text 8")
        for text in SpamList:
            self.SpamtextCombo.InsertItem(0, text)
        self.SpamtextCombo.Hide()
        self.SpamTextButton = self.comp.HideButton(None, '', 'Spam-Text', wndMgr.GetScreenWidth()-115, 480, lambda : self.SpamText(), eXLib.PATH + 'OpenBot/Images/Hackbar/spam_0.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/spam_1.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/spam_0.tga')

        self.GoForward = self.comp.HideButton(None, '', '', wndMgr.GetScreenWidth()-230, 30, lambda : self.TeleportInDirection(1), eXLib.PATH + 'OpenBot/Images/Shortcuts/Arrow/tele_up_0.tga', eXLib.PATH + 'OpenBot/Images/Shortcuts/Arrow/tele_up_1.tga', eXLib.PATH + 'OpenBot/Images/Shortcuts/Arrow/tele_up_0.tga')
        self.GoBack = self.comp.HideButton(None, '', '', wndMgr.GetScreenWidth()-229, 92, lambda : self.TeleportInDirection(2), eXLib.PATH + 'OpenBot/Images/Shortcuts/Arrow/tele_down_0.tga', eXLib.PATH + 'OpenBot/Images/Shortcuts/Arrow/tele_down_1.tga', eXLib.PATH + 'OpenBot/Images/Shortcuts/Arrow/tele_down_0.tga')
        self.GoRight = self.comp.HideButton(None, '', '', wndMgr.GetScreenWidth()-196, 58, lambda : self.TeleportInDirection(3), eXLib.PATH + 'OpenBot/Images/Shortcuts/Arrow/tele_right_0.tga', eXLib.PATH + 'OpenBot/Images/Shortcuts/Arrow/tele_right_1.tga', eXLib.PATH + 'OpenBot/Images/Shortcuts/Arrow/tele_right_0.tga')
        self.GoLeft = self.comp.HideButton(None, '', '', wndMgr.GetScreenWidth()-290, 59, lambda : self.TeleportInDirection(4), eXLib.PATH + 'OpenBot/Images/Shortcuts/Arrow/tele_left_0.tga', eXLib.PATH + 'OpenBot/Images/Shortcuts/Arrow/tele_left_1.tga', eXLib.PATH + 'OpenBot/Images/Shortcuts/Arrow/tele_left_0.tga')

        self.SettingsButton = self.comp.Button(self.OpenBotBoard, '', 'Settings', 9, 10, self.Generel, eXLib.PATH + 'OpenBot/Images/Hackbar/sett_0.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/sett_1.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/sett_2.tga')
        self.LevelbotButton = self.comp.Button(self.OpenBotBoard, '', 'Levelbot', 8, 43, self.OnLevelbot, eXLib.PATH + 'OpenBot/Images/Hackbar/sword_0.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/sword_1.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/sword_0.tga')
        #self.BuffbotButton = self.comp.Button(self.OpenBotBoard, '', 'Buffbot', 8, 78, self.BuffBot, eXLib.PATH + 'OpenBot/Images/Hackbar/buff_0.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/buff_1.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/buff_0.tga')
        self.SpambotButton = self.comp.Button(self.OpenBotBoard, '', 'Spambot', 8, 253, self.Spambot, eXLib.PATH + 'OpenBot/Images/Hackbar/spam_0.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/spam_1.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/spam_0.tga')
        if DEBUG:
            self.MiningBotButton = self.comp.Button(self.OpenBotBoard, '', 'MiningBot', 8, 323, self.MiningBot, eXLib.PATH + 'OpenBot/Images/Hackbar/ore_slot_0.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/ore_slot_1.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/ore_slot_0.tga')
        self.SearchBotButton = self.comp.Button(self.OpenBotBoard, '', 'SearchBot', 10, 113, self.SearchBot, eXLib.PATH + 'OpenBot/Images/Hackbar/search_0.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/search_1.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/search_0.tga')
        self.ShopCreatorButton = self.comp.Button(self.OpenBotBoard, '', 'Shopbot', 8, 148, self.ShopCreator, eXLib.PATH + 'OpenBot/Images/Hackbar/shop_0.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/shop_1.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/shop_0.tga')
        self.FishingBotButton = self.comp.Button(self.OpenBotBoard, '', 'FishingBot', 8, 78, self.FishingBot, eXLib.PATH + 'OpenBot/Images/Hackbar/fishing_0.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/fishing_1.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/fishing_0.tga')
        self.TeleButton = self.comp.Button(self.OpenBotBoard, '', 'Teleport', 10, 218, self.TeleportHack, eXLib.PATH + 'OpenBot/Images/Hackbar/teleport_0.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/teleport_1.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/teleport_0.tga')
        self.InventoryButton = self.comp.Button(self.OpenBotBoard, '', 'Manager', 10, 183, self.InventoryManager, eXLib.PATH + 'OpenBot/Images/Hackbar/inventory_0.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/inventory_1.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/inventory_0.tga')
        self.RunPythonButton = self.comp.Button(self.OpenBotBoard, '', 'Run-Python', 10, 288, self.RunPython, eXLib.PATH + 'OpenBot/Images/Shortcuts/loadpy_0.tga', eXLib.PATH + 'OpenBot/Images/Shortcuts/loadpy_1.tga', eXLib.PATH + 'OpenBot/Images/Shortcuts/loadpy_0.tga')
        self.RadarButton = self.comp.Button(self.OpenBotBoard, '', 'Radar', 8, 323, self.OnRadar, eXLib.PATH + 'OpenBot/Images/Hackbar/radar_0.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/radar_1.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/radar_0.tga')
        self.SkillbotButton = self.comp.Button(self.OpenBotBoard, '', 'Skillbot', 8, 358, self.OnSkillbot, eXLib.PATH + 'OpenBot/Images/Hackbar/skill_0.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/skill_1.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/skill_0.tga')
        self.FarmbotButton = self.comp.Button(self.OpenBotBoard, '', 'Farmbot', 8, 393, self.OnFarmingBot, eXLib.PATH + 'OpenBot/Images/Hackbar/farm_0.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/farm_1.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/farm_0.tga')
        self.AutoDungeonButton = self.comp.Button(self.OpenBotBoard, '', 'AutoDungeon', 8, 428, self.OnAutoDungeon, eXLib.PATH + 'OpenBot/Images/Hackbar/dt_0.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/dt_1.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/dt_0.tga')
        self.EnergyBotButton = self.comp.Button(self.OpenBotBoard, '', 'EnergyBot', 8, 463, self.OnEnergyBot, eXLib.PATH + 'OpenBot/Images/Hackbar/energy_0.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/energy_1.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/energy_0.tga')
        self.ActionBotButton = self.comp.Button(self.OpenBotBoard, '', 'ActionBot', 8, 498, self.OnActionBot, eXLib.PATH + 'OpenBot/Images/Hackbar/action_0.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/action_1.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/action_0.tga')

        if DEBUG:
            self.AnalyzerButton = self.comp.Button(self.OpenBotBoard, '', 'Packet Analyzer', 8, 358, self.PacketAnalyzer, eXLib.PATH + 'OpenBot/Images/Hackbar/analyzer_0.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/analyzer_1.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/analyzer_0.tga')
        else:
            self.CopyrightLabel = self.comp.TextLine(self.OpenBotBoard, '', 3, 320, self.comp.RGB(255, 255, 0))
        #self.InfoButton = self.comp.Button(self.OpenBotBoard, '', 'Info', 10, 500, self.Info, eXLib.PATH + 'OpenBot/Images/Hackbar/info_0.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/info_1.tga', eXLib.PATH + 'OpenBot/Images/Hackbar/info_0.tga')
    def OpenHackbar(self):
        if self.Hackbar:
            self.Hackbar = 0
            self.ShowHackbarButton.Show()
            self.HideHackbarButton.Hide()
            self.OpenBotBoard.Hide()
        else:
            self.Hackbar = 1
            self.ShowHackbarButton.Hide()
            self.HideHackbarButton.Show()
            self.OpenBotBoard.Show()

    def OpenTeleport(self):
        if self.Teleport:
            self.Teleport = 0
            self.GoForward.Hide()
            self.GoBack.Hide()
            self.GoRight.Hide()
            self.GoLeft.Hide()
        else:
            self.Teleport = 1
            self.GoForward.Show()
            self.GoBack.Show()
            self.GoRight.Show()
            self.GoLeft.Show()


    def OpenShortCuts(self):
        if player.GetName() == "":
            #return
            pass
        if self.ShortCuts:
            self.ShortCuts = 0
            self.GhostButton.Hide()
            self.CrashButton.Hide()
            self.TeleportButton.Hide()
            self.ZoomButton.Hide()
            self.NoFogButton.Hide()
            self.SpamTextButton.Hide()
            self.SpamtextCombo.Hide()
        else:
            self.ShortCuts = 1
            self.GhostButton.Show()
            self.CrashButton.Show()
            self.TeleportButton.Show()
            self.ZoomButton.Show()
            self.NoFogButton.Show()
            self.SpamTextButton.Show()
            self.SpamtextCombo.Show()

    def Generel(self):
        Settings.switch_state()
    def OnLevelbot(self):
        Levelbot.switch_state()
    #def BuffBot(self):
        #self.buff.switch_state()
    def Spambot(self):
        self.spam.switch_state()
    def PacketAnalyzer(self):
        if DEBUG:
            self.filter.switch_state()

    def MiningBot(self):
        if DEBUG:
            MiningBot.switch_state()
    def SearchBot(self):
        ShopSearcher.switch_state()
    def ShopCreator(self):
        Shopcreator.switch_state()
    def TeleportHack(self):
        self.tele.switch_state()

    def OnFarmingBot(self):
        FarmingBot.switch_state()

    def OnAutoDungeon(self):
        AutoDungeon.switch_state()

    def OnChannelSwitcher(self):
        ChannelSwitcher.switch_state()

    def OnSkillbot(self):
        Skillbot.switch_state()

    def OnEnergyBot(self):
        self.energy_bot.switch_state()
    def OnActionBot(self):
        self.action_bot.switch_state()

    def OnRadar(self):
        self.radar.switch_state()
    def InventoryManager(self):
        Inventorymanager.switch_state()
    def FishingBot(self):
        FishingBot.switch_state()

    def RunPython(self):
        self.python_manager.switch_state()


    def GhostMod(self):
        if player.GetStatus(player.HP) < 1:
            chr.Revive()
        else:
            chat.AppendChat(7,"[OpenBot-Mod] You have to die and than you can restart in the Ghost-Mod!")

    def CloseRequest(self):
        self.QuestionDialog = uiCommon.QuestionDialog()
        self.QuestionDialog.SetText("Do You want to quit Metin2 immediately?")
        self.QuestionDialog.SetAcceptEvent(ui.__mem_func__(self.Close))
        self.QuestionDialog.SetCancelEvent(ui.__mem_func__(self.CancelQuestionDialog))
        self.QuestionDialog.Open()
        
    def Close(self):
        app.Abort()
    def CancelQuestionDialog(self):
        self.QuestionDialog.Close()
        self.QuestionDialog = None

    def Zoom(self):
        app.SetCameraMaxDistance(12000)

    def NoFog(self):
        app.SetMinFog(12000)


    def SpamText(self):
        Type = FileManager.ReadConfig("Type")
        SpamText = FileManager.ReadConfig("Text"+str(self.SpamtextCombo.GetSelectedIndex()+1))

        if Type == "Normal":
            net.SendChatPacket(str(SpamText), chat.CHAT_TYPE_TALKING)
        else:
            net.SendChatPacket(str(SpamText), chat.CHAT_TYPE_SHOUT)

    def TeleportInDirection(self, direction):
        (x, y, z) = player.GetMainCharacterPosition()
        if direction == 1:
            trueX = x
            trueY = y - 2400
        elif direction == 2:
            trueX = x
            trueY = y + 2400
        elif direction == 3:
            trueX = x + 2400
            trueY = y
        elif direction == 4:
            trueX = x - 2400
            trueY = y
        chr.SelectInstance(net.GetMainActorVID())
        chr.SetPixelPosition(int(trueX), int(trueY), int(z))
        eXLib.SendStatePacket(trueX,trueY,0,eXLib.CHAR_STATE_STOP,0)
        eXLib.SendStatePacket(trueX+100,trueY+100,0,1,0)
        eXLib.SendStatePacket(trueX-100,trueY-100,0,1,0)
        eXLib.SendStatePacket(trueX,trueY,0,1,0)
        #player.SetSingleDIKKeyState(app.DIK_UP, TRUE)
        #player.SetSingleDIKKeyState(app.DIK_UP, FALSE)
try:
    app.Shop.Close()
except:
    pass
app.Shop = OpenBotHackbarDialog()
KeyBot.instance.enableButton.SetOn()
KeyBot.instance.Start()
