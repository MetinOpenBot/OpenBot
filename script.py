from OpenBot.Modules.OpenLog import DebugPrint
import OpenBot.hackbar
#import GuiEditor
#import dump_functions
from OpenBot.Modules.Actions import ActionLoader, ActionBot

#actionLoader = ActionLoader.ActionLoader()

#result = actionLoader.LoadActionsFromFile('GoToFirstCity.action')

"""
raw_actions = {'actions':[
    {'name': 'Go to first city',
    'function': 'MoveToPosition',
    'function_args': [(59000, 68900), 'metin2_first_city'],
    'requirements': {'IS_ON_POSITION': [59000, 68900], 
                    'IS_IN_MAP': ['metin2_first_city']}
        },
    {'name': 'Go to circle',
    'function': 'MoveToPosition',
    'function_args': [(63969, 64751), 'metin2_first_city'],
    'requirements': {'IS_ON_POSITION': [63969, 64751], 
                    'IS_IN_MAP': ['metin2_first_city']}
        }
    ]
}


actionLoader = ActionLoader.ActionLoader()
cleared_action = actionLoader.ValidateRawActions(raw_actions)
DebugPrint(str(cleared_action))

for action in cleared_action:
    ActionBot.instance.AddNewAction(action)
"""