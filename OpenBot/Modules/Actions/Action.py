from OpenBot.Modules import OpenLib, OpenLog
import ActionRequirementsCheckers

# Parents

FARMING_BOT = 'farming_bot'


# RETURNINGS
NOTHING = 'NOTHING'
NEXT_ACTION = 'NEXT_ACTION'
ERROR = 'ERROR'

DISCARD_PREVIOUS = 'DISCARD_PREVIOUS'
REQUIREMENTS_NOT_DONE = 'REQUIREMENTS_NOT_DONE'
on_success_keys = [NOTHING, NEXT_ACTION, ERROR, DISCARD_PREVIOUS, REQUIREMENTS_NOT_DONE]

class Action:

    def __init__(self, function, _id=0, callback=None, callback_on_failed=None, interrupt_function=None, name='None', function_args=[],
     callback_args=[], interruptors_args=[], interrupt_function_args=[], requirements=[], on_success=[], on_failed=[], interruptors=[], call_only_once=False):
        self.id = _id
        self.call_only_once = call_only_once
        self.called = False
        if name == 'None':
            self.name = function.__name__
        else:
            self.name = name

        self.function_args = function_args # ...
        self.callback_args = callback_args # ...
        self.interruptors_args = interruptors_args
        self.interrupt_function_args = interrupt_function_args
        self.requirements = requirements # List of requirements in ActionRquirementsCheckers
        self.on_success = on_success # on_success flags from ActionBot
        self.on_failed = on_failed # on_failed flags from ActionBot
        self.interruptors = interruptors
        
        self.function = function # Function is... ?
        self.callback = callback # Callback is a function
        self.callback_on_failed = callback_on_failed
        self.interrupt_function = interrupt_function

    def CallCallback(self):
        if self.callback_args:
            self.callback(self.callback_args)
        else:
            if callable(self.callback):
                self.callback()

    def Interrupt(self):
        if self.interrupt_function is not None:
            if self.interrupt_function_args:
                return self.interrupt_function(self.interrupt_function_args)
            else:
                return self.interrupt_function()
        else:
            OpenLog.DebugPrint('There is no Interruptor function, but there are interruptors!')


    def CallFunction(self):
        if self.interruptors:
            if len(self.interruptors_args) == len(self.interruptors):
                for interruptor in range(len(self.interruptors)):
                    if self.interruptors[interruptor](self.interruptors_args[interruptor]):
                        return self.Interrupt()
            else:
                if not self.interruptors_args:
                    for interruptor in self.interruptors:
                        if interruptor():
                            return self.Interrupt()
                else:
                    OpenLog.DebugPrint('There is different length in interruptors_args and interruptors')

        if self.call_only_once and not self.called:
            OpenLog.DebugPrint('Executing action function')
            if self.function_args:
                action_result = self.function(self.function_args)
            else:
                action_result = self.function()
            self.called = True

        elif self.call_only_once and self.called:
            on_success = self.CheckOnSuccesList()
            requirements_done = self.CheckRequirements()
            if on_success:
                if requirements_done:
                    return on_success
                return REQUIREMENTS_NOT_DONE

        elif not self.call_only_once:
            OpenLog.DebugPrint('Executing action function')
            if self.function_args:
                action_result = self.function(self.function_args)
            else:
                action_result = self.function()
       
        if type(action_result) == bool:
            if action_result:
                on_success = self.CheckOnSuccesList()
                requirements_done = self.CheckRequirements()
                if on_success:
                    if requirements_done:
                        return on_success
                    return REQUIREMENTS_NOT_DONE
                else:
                    if requirements_done:
                        return NEXT_ACTION
                    return REQUIREMENTS_NOT_DONE
            else:
                on_failed = self.CheckOnFailedList()
                return on_failed
        else:
            return action_result

    
    def CheckRequirements(self):
        for requirement in self.requirements:
            if requirement == ActionRequirementsCheckers.IS_IN_MAP:
                if not ActionRequirementsCheckers.isInMaps(self.requirements[requirement]):
                    return False
            
            elif requirement == ActionRequirementsCheckers.IS_ON_POSITION:
                if not ActionRequirementsCheckers.isOnPosition(self.requirements[requirement]):
                    return False
            
            elif requirement == ActionRequirementsCheckers.IS_NEAR_POSITION:
                if not ActionRequirementsCheckers.isNearPosition(self.requirements[requirement]):
                    return False
            
            elif requirement == ActionRequirementsCheckers.IS_NEAR_INSTANCE:
                if not ActionRequirementsCheckers.isNearInstance(self.requirements[requirement]):
                    return False
            
            elif requirement == ActionRequirementsCheckers.IS_IN_CHANNEL:
                if not ActionRequirementsCheckers.IsInChannel(self.requirements[requirement]):
                    return False

        return True

    def CheckOnSuccesList(self):
        for succes_key in self.on_success:
            if callable(succes_key):
                if succes_key():
                    return NEXT_ACTION
            elif type(succes_key) == str:
                if succes_key == NEXT_ACTION:
                    return NEXT_ACTION
                elif succes_key == DISCARD_PREVIOUS:
                    return DISCARD_PREVIOUS
        return NEXT_ACTION

    def CheckOnFailedList(self):
        for failed_key in self.on_failed:
            if callable(failed_key):
                if failed_key():
                    return NEXT_ACTION
            elif type(failed_key) == str:
                if failed_key == NEXT_ACTION:
                    return NEXT_ACTION
        return NEXT_ACTION

