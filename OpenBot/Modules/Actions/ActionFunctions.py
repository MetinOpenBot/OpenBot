from time import sleep, time
from OpenBot.Modules import MapManager, Movement, OpenLib
from OpenBot.Modules.Actions import Action, ActionRequirementsCheckers
from OpenBot.Modules import NPCInteraction
from OpenBot.Modules.NPCInteraction import NPCAction
from OpenBot.Modules.OpenLog import DebugPrint
import eXLib
import player, net, chr, chat, background, item

# This actions is used for clearing all visible monsters untill there is something to kill
def ClearFloor(args):
    player.SetAttackKeyState(False)
    x, y = args[0]
    my_x,my_y, z = player.GetMainCharacterPosition()
    path = eXLib.FindPath(my_x,my_y,x,y)
    if not path:
        Movement.StopMovement()
        return True
    is_monster_nearby = OpenLib.IsMonsterNearby()
    if OpenLib.isPlayerCloseToPosition(x, y) and not is_monster_nearby:
        Movement.StopMovement()
        return True

    if not is_monster_nearby:
        action_dict = {'function_args': [(x, y)], # position
        'name': 'Go to center of floor',
        'function': MoveToPosition,
        'requirements': { ActionRequirementsCheckers.IS_ON_POSITION: (x, y)},
        'on_failed': [Action.NEXT_ACTION],
        }
        return action_dict

    vid = OpenLib.GetNearestMonsterVid()
    action_dict = {'function_args': [0, vid], # position
    'function': Destroy,
    'name': 'Kill mob',
    'requirements': {},
    'on_success': [Action.NEXT_ACTION],
    }
    return action_dict

# This action is attacking choosed mob by race or id
def Destroy(args):
    if args[1]:
        instance_vid = args[1]
    else:
        instance_vid = 0
        for vid in eXLib.InstancesList:
            chr.SelectInstance(vid)
            if chr.GetRace() == args[0]:
                instance_vid = vid
                break

    if eXLib.IsDead(instance_vid):
        player.SetAttackKeyState(False)
        return Action.NEXT_ACTION

    if not OpenLib.isPlayerCloseToInstance(instance_vid):
        x, y, z = chr.GetPixelPosition(instance_vid)
        action_dict = {
            'function': MoveToPosition,
            'function_args': [(x, y)],
            'name': 'Going to enemy',
            'on_success': [Action.NEXT_ACTION],
            'interruptors_args': [instance_vid],
            'interruptors': [ActionRequirementsCheckers.IsDead],
            'interrupt_function': lambda: Action.NEXT_ACTION
        }
        return action_dict

    vid_life_status = OpenLib.AttackTarget(instance_vid)

    if vid_life_status == OpenLib.TARGET_IS_DEAD:
        player.SetAttackKeyState(False)
        return Action.NEXT_ACTION

    elif vid_life_status == OpenLib.ATTACKING_TARGET:
        return Action.NOTHING

    elif vid_life_status == OpenLib.MOVING_TO_TARGET:
        return Action.NOTHING
    
    return False

# This action returing true if mob of giving id is in sight
def Find(args):
    for vid in eXLib.InstancesList:
        chr.SelectInstance(vid)
        if chr.GetRace() == args[0]:
            return True
    return False

def MoveToPosition(args):
    position = args[0]
    if OpenLib.isPlayerCloseToPosition(position[0], position[1], 200):
        return Action.NEXT_ACTION
    if len(args) > 1:
        error = Movement.GoToPositionAvoidingObjects(position[0], position[1], mapName=args[1])
    else:
        error = Movement.GoToPositionAvoidingObjects(position[0], position[1], mapName=background.GetCurrentMapName())

    if error == None:
        return Action.ERROR

    #DebugPrint('Going to ' + str(position))
    return Action.NOTHING

def MoveToVID(args):
    if eXLib.IsDead(args[0]):
        return Action.NEXT_ACTION
    x, y, z = chr.GetPixelPosition(args[0])
    return MoveToPosition([(x, y)])

def UsingItemOnInstance(args):
    instance = args[0]
    item_slot = args[1]
    if OpenLib.isPlayerCloseToInstance(instance, max_dist=500):
        net.SendGiveItemPacket(instance, player.SLOT_TYPE_INVENTORY, item_slot, player.GetItemCount(item_slot))
        OpenLib.skipAnswers([0, 0], True)
        return True

    x, y, z = chr.GetPixelPosition(instance)
    action_dict = {'function_args': [(x, y)], # position
                    'function': MoveToPosition,
                    'requirements': { ActionRequirementsCheckers.IS_ON_POSITION: (x, y)},
                    'on_failed': [Action.NEXT_ACTION],
                    }
    return action_dict

def OpenAllSeals(args):
    closest_seal = OpenLib.getClosestInstance([OpenLib.OBJECT_TYPE])
    if closest_seal < 0:
        return True

    slot_with_key = OpenLib.GetItemByID(50084)
    if slot_with_key >= 0:
        action_dict = {'function_args': [closest_seal, slot_with_key], # position
                        'function': UsingItemOnInstance,
                        'on_success': [Action.NEXT_ACTION],
                        'on_failed': [Action.NEXT_ACTION],

                        }
        return action_dict
        

    if OpenLib.IsMonsterNearby():
        x, y = args[0]
        #DebugPrint('Clearing the floor')
        action_dict = { 'function_args': [(x, y)], # center position of area 
                        'function': ClearFloor,
                        'requirements': {ActionRequirementsCheckers.IS_NEAR_POSITION: (x, y, 100)},
                        'on_success': [Action.NEXT_ACTION],
                        'interrupt_function': lambda: Action.NEXT_ACTION,
                        'interruptors': [ActionRequirementsCheckers.HasItem],
                        'interruptors_args': [50084]
                    }

        return action_dict
    return Action.NOTHING

def UpgradeDeamonTower(args):
    item_slot = args
    net.SendRefinePacket(item_slot, 4)
    return True

def GoBuyItemsFromNPC(args):
    items_slots_list_to_buy = args[0]
    npc_id = args[1]
    npc_position_x, npc_position_y = args[2]
    callback = args[3]

    if not OpenLib.isPlayerCloseToPosition(npc_position_x, npc_position_y):
        action_dict = {'function_args': [(npc_position_x, npc_position_y)], # position
                        'function': MoveToPosition,
                        'requirements': { ActionRequirementsCheckers.IS_ON_POSITION: (npc_position_x, npc_position_y)}
                        }
        return action_dict

    npc = NPCAction(npc_id, event_answer=[1])
    NPCInteraction.RequestBusinessNPCClose(items_slots_list_to_buy, [], npc, callback)
    return True
    
def GetEnergyFromAlchemist(args):
    items_id_to_use = args[0]
    alchemist_id = args[1]
    position_x, position_y = args[2]
    if not OpenLib.isPlayerCloseToPosition(position_x, position_y):
        action_dict = {'function_args': [(position_x, position_y), OpenLib.GetPlayerEmpireFirstMap()], # position
                        'function': MoveToPosition,
                        'requirements': { ActionRequirementsCheckers.IS_ON_POSITION: (position_x, position_y)}
                        }
        return action_dict
    

    for _id in items_id_to_use:
        item_slot = OpenLib.GetItemByID(_id)
        if item_slot < 0:
            continue
        alchemist_vid = OpenLib.GetInstanceByID(alchemist_id)
        if alchemist_vid != -1:
            action_dict = {'function_args': [alchemist_vid, item_slot], # position
                            'function': UsingItemOnInstance,
                            'on_success': [Action.NEXT_ACTION],
                            'on_failed': [Action.NEXT_ACTION],
                            }
            return action_dict
    return True

def ChangeEnergyToCrystal(args):
    alchemist_id = args[0]
    npc_position_x, npc_position_y = args[1]
    map_name = args[2]
    if not OpenLib.isPlayerCloseToPosition(npc_position_x, npc_position_y, 1000):
        action_dict = {'function_args': [(npc_position_x, npc_position_y), 250], # position
                        'function': MoveToPosition,
                        'requirements': { ActionRequirementsCheckers.IS_ON_POSITION: (npc_position_x-50, npc_position_y-50)},
                        'on_success': [Action.NEXT_ACTION],
                        }
        return action_dict
    energy_crystals = OpenLib.GetItemsSlotsByID([51001])
    DebugPrint(str(energy_crystals))

    if not energy_crystals:
        return True

    #energy_crystal = OpenLib.GetItemByID(51001)
    for energy_crystal in energy_crystals[51001]:
        DebugPrint(str(energy_crystal))
        if player.GetItemCount(energy_crystal) >= 30:
            answer = [5,254,254,0,254]
            action_dict = { 'function_args': [alchemist_id, (npc_position_x, npc_position_y), answer, map_name], # ID, event_answer, posiiton of npc, npc's map
                            'function': TalkWithNPC,
                            'on_success': [Action.NEXT_ACTION],
                            'requirements': {},

                }
            return action_dict
    return True

def TalkWithNPC(args):
    npc_id = args[0]
    npc_position_x, npc_position_y = args[1]
    event_answer = args[2]
    if len(args) > 3:
        map_name = args[3]
    else:
        map_name = background.GetCurrentMapName()

    if npc_position_x == 0 and npc_position_y == 0:
        current_map = background.GetCurrentMapName()
        result = MapManager.GetNpcFromMap(current_map, npc_id)
        if result is None:
           return Action.NEXT_ACTION
        else:
            npc_position_x, npc_position_y = result

    if not OpenLib.isPlayerCloseToPosition(npc_position_x, npc_position_y, 1000):
        action_dict = {'function_args': [(npc_position_x, npc_position_y), map_name], # position
                        'function': MoveToPosition,
                        'requirements': { ActionRequirementsCheckers.IS_NEAR_POSITION: (npc_position_x, npc_position_y, 1000),
                                          ActionRequirementsCheckers.IS_IN_MAP: [map_name]}
                        }
        return action_dict
    
    vid = OpenLib.GetInstanceByID(npc_id)
    if vid >= 0:
        net.SendOnClickPacket(vid)
        OpenLib.skipAnswers(event_answer, True)
        return Action.NEXT_ACTION
    return False
    
def MineOre(args):
    selectedOre = args[0]
    is_curr_mining = args[1]()
    if eXLib.IsDead(selectedOre):
        return Action.NEXT_ACTION
    

    can_mine = False
    idx = player.GetItemIndex(player.EQUIPMENT, item.EQUIPMENT_WEAPON)
    if idx != 0:
        item.SelectItem(idx)
        if item.GetItemType() == item.ITEM_TYPE_PICK:
            can_mine = True
    
    if not can_mine:
        pickaxe_slot = OpenLib.GetItemByID(29101)
        if pickaxe_slot > -1:
            chat.AppendChat(3, 'pickaxe slot '+str(pickaxe_slot))
            net.SendItemUsePacket(pickaxe_slot)   
        else:
            can_mine = False

    if not can_mine:
        idx = player.GetItemIndex(player.EQUIPMENT, item.EQUIPMENT_WEAPON)
        if idx != 0:
            item.SelectItem(idx)
            if item.GetItemType() == item.ITEM_TYPE_PICK:
                can_mine = True

    if not OpenLib.isPlayerCloseToInstance(selectedOre):
        action_dict = {'function_args': [selectedOre],
                        'function': MoveToVID,
                        'requirements': {ActionRequirementsCheckers.isNearInstance: [selectedOre]},
                        'on_success': [Action.NEXT_ACTION]}
        return action_dict
                    
    if not is_curr_mining and can_mine:
        net.SendOnClickPacket(selectedOre)
        DebugPrint('Digging')
    
    return False
    
def LookForBlacksmithInDeamonTower(args):
    go_above_six_stage = args[0]
    item_index_to_upgrade = args[1]

    blacksmiths_id = [20074, 20075, 20076]

    for vid in eXLib.InstancesList:
        chr.SelectInstance(vid)
        for _id in blacksmiths_id:
            if chr.GetRace() == _id:
                x, y, z = chr.GetPixelPosition(vid)
                if not OpenLib.isPlayerCloseToPosition(x, y, 500):
                    action_dict = {
                        'function_args': [(x, y)],
                        'function': MoveToPosition,
                        'requirements': { ActionRequirementsCheckers.IS_ON_POSITION: (x, y)},
                        'on_success': [Action.NEXT_ACTION]
                    }

                    return action_dict

                if item_index_to_upgrade >= 0:
                    UpgradeDeamonTower(item_index_to_upgrade)
                
                if go_above_six_stage:
                    if player.GetStatus(player.LEVEL) < 75:
                        answer = [0, 254, 0]
                    else:
                        answer = [1, 1, 1, 1]
                
                else:
                    if player.GetStatus(player.LEVEL) < 75:
                        answer = [1, 1, 1]
                    else:
                        answer = [0, 254, 2]
                    
                chat.AppendChat(3, answer)
                if answer:
                    action_dict = {
                        'function_args': [_id, (x, y), answer, 'metin2_map_deviltower1'],
                        'function': TalkWithNPC,
                        'on_success': [Action.NEXT_ACTION],
                        'requirements': {},
                    }
                    return action_dict
                return Action.NEXT_ACTION

            
    return Action.NEXT_ACTION

def FindMapInDT(args):
    center_position = args[0]
    correct_map = OpenLib.GetItemByID(30302)
    unknow_old_chest = OpenLib.GetItemByID(30300)
    
    if correct_map >=0:
        net.SendItemUsePacket(correct_map)
        return Action.NEXT_ACTION

    if unknow_old_chest >=0:
        net.SendItemUsePacket(unknow_old_chest)


    if not OpenLib.IsMonsterNearby():
        if OpenLib.isPlayerCloseToPosition(center_position[0], center_position[1], 300):
            return Action.NOTHING
        else:
            action_dict = {'function_args': [(center_position[0], center_position[1]), 250], # position
                            'function': MoveToPosition,
                            'requirements': { ActionRequirementsCheckers.IS_ON_POSITION: (center_position[0], center_position[1])},
                            'on_success': [Action.NEXT_ACTION],
                            }
            return action_dict

    action_dict = { 'function_args': [(center_position[0], center_position[1])], # center position of area 
                'function': ClearFloor,
                'requirements': {ActionRequirementsCheckers.IS_NEAR_POSITION: (center_position[0], center_position[1])},
                'on_success': [Action.NEXT_ACTION],
                'interruptors_args': [30302, 30300],
                'interruptors': [ActionRequirementsCheckers.HasItem, ActionRequirementsCheckers.HasItem],
                'interrupt_function': lambda: Action.NEXT_ACTION
            }

    return action_dict    

def OpenASealInMonument(args):
    center_position = args[0]
    correct_key = OpenLib.GetItemByID(30304)
    player_x, player_y, player_z = player.GetMainCharacterPosition()

    if not eXLib.FindPath(player_x, player_y, center_position[0], center_position[1]):
        return True

    if correct_key >=0:
        monument = OpenLib.getClosestInstance([OpenLib.OBJECT_TYPE])
        action_dict = {'function_args': [monument, correct_key], # position
                        'function': UsingItemOnInstance,
                        'on_success': [Action.NEXT_ACTION],
                        'on_failed': [Action.NEXT_ACTION],
                        }
        return action_dict
        
    
    action_dict = { 'function_args': [(center_position[0], center_position[1])], # center position of area 
                'function': ClearFloor,
                'requirements': {ActionRequirementsCheckers.IS_NEAR_POSITION: (center_position[0], center_position[1], 100)},
                'on_success': [Action.NEXT_ACTION],
                'interrupt_function': lambda: Action.NEXT_ACTION,
                'interruptors': [ActionRequirementsCheckers.HasItem],
                'interruptors_args': [30304]
            }

    return action_dict  

def ExchangeTrashItemsToEnergyFragments(args):
    from OpenBot.Modules import Settings
    first_map = OpenLib.GetPlayerEmpireFirstMap()

    x, y = MapManager.GetNpcFromMap(first_map, 20001)
    return {'function_args': [Settings.instance.sellItems, 20001, (x, y)], # position
            'function': GetEnergyFromAlchemist,
            'on_success': [Action.NEXT_ACTION],
            }

def ChangeMap(args):
    move_position_x, move_position_y = args[0]
    map_name = args[1]
    npc_id = args[2]
    event_answer = args[3]
    map_destination_name = args[4]

    if map_destination_name == map_name:
        return Action.NEXT_ACTION

    DebugPrint('Changing the map')
    if map_name == background.GetCurrentMapName() and not npc_id and not event_answer:
        DebugPrint('Going go position')
        if not OpenLib.isPlayerCloseToPosition(move_position_x, move_position_y):
            DebugPrint('Returning move to position action')
            return {
                'function_args': [(move_position_x, move_position_y), map_name],
                'name': 'Going to teleport point',
                'function': MoveToPosition,
                #'on_success': [Action.NEXT_ACTION],
                #'requirements': {ActionRequirementsCheckers.IS_ON_POSITION: [move_position_x, move_position_y]}
            }
        DebugPrint('going to next actions')
        return Action.NEXT_ACTION

    if map_destination_name != background.GetCurrentMapName():
        DebugPrint('Returning talk with npc')
        return {
            'function_args': [npc_id,(0, 0), event_answer],
            'name': 'Talking to teleport',
            'function': TalkWithNPC,
            'on_success': [Action.NEXT_ACTION],
        }
    return Action.NEXT_ACTION
    
def ChangeChannel(args):
    channel_id = args[0]

    from OpenBot.Modules import ChannelSwitcher
    ChannelSwitcher.instance.GetChannels()

    if not channel_id:
        DebugPrint('Channel id is ' + str(channel_id))
        return Action.ERROR

    if OpenLib.GetCurrentChannel() == channel_id:
        return Action.NEXT_ACTION

    if 0 < channel_id > len(ChannelSwitcher.instance.channels):
        return Action.ERROR
    
    if ChannelSwitcher.instance.currState != ChannelSwitcher.STATE_CHANGING_CHANNEL:
        DebugPrint('Changing channel to ' + str(channel_id) )
        ChannelSwitcher.instance.ChangeChannelById(channel_id)
        return True
