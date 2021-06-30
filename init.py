#Responsible for inputing the right methods
#DON'T RUN SCRIPTS FROM ON HERE

import sys, os
import chatm2g as _chat
import playerm2g2 as _player
import m2netm2g as _net
import chrmgrm2g as _chrmgr
import eXLib
import chr,app

sys.modules['player'] = _player
sys.modules['net'] = _net
sys.modules['chat'] = _chat
sys.modules['chrmgr'] = _chrmgr


def SetSingleDIKKeyState(key,state):
    if state == 1:
        _player.OnKeyDown(key)
    else:
        _player.OnKeyUp(key)

def SetAttackKeyState(state):
    if state == 1:
        _player.OnKeyDown(app.DIK_SPACE)
    else:
        _player.OnKeyUp(app.DIK_SPACE)

setattr(chr, 'GetPixelPosition', eXLib.GetPixelPosition)
setattr(chr, 'MoveToDestPosition', eXLib.MoveToDestPosition)
setattr(_net, 'GetMainActorVID', _player.GetMainCharacterIndex)
setattr(_player, 'SetSingleDIKKeyState', SetSingleDIKKeyState)
setattr(_player, 'SetAttackKeyState', SetAttackKeyState)

command = "mklink /d " + '"' + eXLib.PATH+"OpenBot" + '"' + " OpenBot"
os.system(command)

#Set Path
folder = eXLib.PATH+"OpenBot"
command = 'mklink /d OpenBot "' + folder +'"'

if os.path.isdir(folder):
    os.system("rmdir /S /Q OpenBot")
elif os.path.isfile(folder):
    os.system("rmdir OpenBot")
os.system(command)
