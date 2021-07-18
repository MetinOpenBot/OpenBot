import eXLib,ui,chr,player,chat,background,app,net
import OpenLib,MapManager,OpenLog




"""
Module of Movement.
Allows to move and to teleport.
"""
TELEPORT_WAIT_TIME = 1 #Time to wait if number of teleports exceds the max_packet paramenter in seconds

STATE_FINISH = 1
STATE_MOVING = 2
STATE_STOPPED = 0

NO_PATH_FOUND = 0
DESTINATION_REACHED = 1
MOVING = 1

MAX_TELEPORT_PACKETS = 60

TIME_STOPPED_ALLOWED = 3

#Tim after each loop
TIME_WAIT = 0.2

TIME_WAIT_MAP_CHANGE = 2

#Callback
def _DestinationReachedCallback():
    mapMovement.SetStateMapChanging()

#Move character across maps
class MapMovementDialog(ui.ScriptWindow):

    STATE_NONE = 0
    STATE_MOVING = 1
    STATE_MAPCHANGING = 2

    def __init__(self):
        ui.ScriptWindow.__init__(self)
        self.Show()
        self.leftLinkList = []
        self.currLink = 0
        self.generalTimer = 0
        self.callback = None
        self.State = self.STATE_NONE

    def SetState(self,state):
        self.State = state

    def Stop(self):
        self.SetState(self.STATE_NONE)

    #Either mapName or list must not be none
    def MoveToMapPosition(self,finalPosition,mapName=None,listLinks=[],callback=None,maxDist=250):
        if len(listLinks) == 0:
            if mapName == None or mapName == background.GetCurrentMapName():
                OpenLog.DebugPrint("[MOVEMENT] Moving to ("+str(finalPosition[0])+","+str(finalPosition[1])+") on " + str(background.GetCurrentMapName()))
                return Movement.GoToPositionAvoidingObjects(finalPosition[0],finalPosition[1],maxDist,callback=callback)
            listLinks = MapManager.GetMapPath(mapName)
            if len(listLinks) == 0:
                OpenLog.DebugPrint("[MOVEMENT] Error no map found by the name: "+str(mapName))
                return None

        self.maxDist = maxDist
        
        
        self.leftLinkList = listLinks
        self.finalPosition = finalPosition
        self.callback = callback
        self.SetStateMoving()

    def SetStateMoving(self):
        self.currLink = self.leftLinkList.pop(0)
        position = self.currLink.npc_action.GetNpcPosition()
        OpenLog.DebugPrint("Moving to ("+str(position[0])+","+str(position[1])+")")
        Movement.GoToPositionAvoidingObjects(position[0],position[1],maxDist=250,callback=None)
        self.SetState(self.STATE_MOVING)

    
    def SetStateMapChanging(self):
        self.SetState(self.STATE_MAPCHANGING)
        

    def StateMapChanging(self):
        curr_map = background.GetCurrentMapName()
        if self.currLink.GetDestMapName() != curr_map:
            self.currLink.CrossMap()
        else:
            if len(self.leftLinkList):
                self.SetStateMoving()
            else:
                Movement.GoToPositionAvoidingObjects(self.finalPosition[0],self.finalPosition[1],maxDist=self.maxDist,callback=self.callback)
                self.callback = None
                self.SetState(self.STATE_NONE)

    def OnUpdate(self):
        if self.State == self.STATE_NONE or not OpenLib.IsInGamePhase():
            return
        val, self.generalTimer = OpenLib.timeSleep(self.generalTimer,TIME_WAIT_MAP_CHANGE)
        if not val:
            return
        if self.State == self.STATE_MOVING:
            if self.currLink.GetOriginMapName() != background.GetCurrentMapName():
                self.SetStateMapChanging()
            return        
        if self.State == self.STATE_MAPCHANGING:
            self.StateMapChanging()

class MovementDialog(ui.ScriptWindow):
    def __init__(self):
        ui.ScriptWindow.__init__(self)
        self.Show()
        self.path = list()
        self.currDestinationX = 0
        self.currDestinationY = 0
        self.state = STATE_STOPPED
        self.stoppedTimer = OpenLib.GetTime()
        self.lastPlayerPos = (0,0)
        self.maxDistanceToDest = 50
        #self.lastMoveX,lastMoveY = (0,0)
        self.generalTimer = 0
        
    def Stop(self):
        self.state = STATE_STOPPED
        self.currDestinationX = 0
        self.currDestinationY = 0
    
    #Move to a specific position using pathfinding
    #maxDist is the maximum distance where the algorithm stop
    #callback is an optional function that will be called when arrive to the target
    def GoToPositionAvoidingObjects(self,x,y,maxDist=250,callback=None):
        self.maxDistanceToDest = maxDist
        self.callback = callback
        if(round(x) != round(self.currDestinationX) or round(y) != round(self.currDestinationY)):
            my_x,my_y,z = player.GetMainCharacterPosition()
            OpenLog.DebugPrint("[MOVEMENT] Finding Path from ("+str(my_x)+","+str(my_y)+") to " + "("+str(x)+","+str(y)+")")
            self.path = eXLib.FindPath(my_x,my_y,x,y)
            OpenLog.DebugPrint("[MOVEMENT] Path Found with "+str(len(self.path)) +" points")
            if(len(self.path)>0):
                self.currDestinationX = x
                self.currDestinationY = y
                self.state = STATE_MOVING
                self.stoppedTimer = OpenLib.GetTime()
                return MOVING
            else:
                self.state = STATE_STOPPED
                self.currDestinationX = 0
                self.currDestinationY = 0
                return NO_PATH_FOUND
        else:
            if(self.state == STATE_FINISH):
                self.state = STATE_STOPPED
                return DESTINATION_REACHED
        return None
            
        
    def GoStraightToPoint(self,x,y):
        OpenLib.RotateMainCharacter(x,y)
        chr.MoveToDestPosition(player.GetMainCharacterIndex(),x, y)
        
    def OnUpdate(self):
        val, self.generalTimer = OpenLib.timeSleep(self.generalTimer,TIME_WAIT)
        if not val or not OpenLib.IsInGamePhase():
            return

        #OpenLog.DebugPrint("[MOVEMENT] - State:" + str(self.state))
        if not (self.state == STATE_MOVING) or len(self.path) == 0:
            return
        
        next_x,next_y = self.path[0]
        my_x,my_y,my_z = player.GetMainCharacterPosition()
        maxdst = 40
        if(len(self.path) == 1):
            maxdst = self.maxDistanceToDest
        if OpenLib.dist(next_x,next_y,my_x,my_y) < maxdst:
            self.path.pop(0)
            if(len(self.path) == 0):
                #Destination Reached
                self.state = STATE_FINISH
                if(self.callback!=None):
                    self.callback()
                    self.callback = None
                self.currDestinationX = 0
                self.currDestinationY = 0
                return
            else:
                next_x,next_y = self.path[0]
        
        if self.lastPlayerPos == (my_x,my_y):
            val, self.stoppedTimer = OpenLib.timeSleep(self.stoppedTimer,TIME_STOPPED_ALLOWED)
            if val:
                #If is stuck
                self.path = eXLib.FindPath(my_x,my_y,self.currDestinationX,self.currDestinationY)
                #player.ClickSkillSlot(9)

        self.lastPlayerPos = (my_x,my_y)
        self.GoStraightToPoint(next_x,next_y)
    
    def __del__(self):
        ui.ScriptWindow.__del__(self)


#Teleport multiple times to prevent resync from server

def TeleportStraightLine(start_x,start_y,end_x,end_y,max_packets=MAX_TELEPORT_PACKETS):
    dst = OpenLib.dist(start_x,start_y,end_x,end_y)
    step = int(dst/OpenLib.MAX_TELEPORT_DIST)

    if step+1>max_packets:
        step = max_packets-1

    x = start_x
    y = start_y
    for i in range(0,step+1):
        _x,_y = OpenLib.getPointsDistance(x,y,end_x,end_y,OpenLib.MAX_TELEPORT_DIST)
        eXLib.SendStatePacket(_x,_y,0,eXLib.CHAR_STATE_STOP,0)
        #chat.AppendChat(3,"Straight Line Teleporting to X->" + str(_x) + "  Y->" + str(_y) + " Distance->" + str(OpenLib.dist(x,y,_x,_y)))
        x,y = (_x,_y)
    
    return (step+1,(x,y))
        
    #Move to a specific position using pathfinding
    #maxDist is the maximum distance where the algorithm stop
    #callback is an optional function that will be called when arrive to the target
    #To move across maps simply provide either a map name or a list of links
    #If both are provided, mapName will be ignored

def GoToPositionAvoidingObjects(x,y,maxDist=250,callback=None,mapName=None,mapLinks=[]):
    """
    Move to a specific position using pathfinding.
    
    Args:
        x ([float]): Destenation X.
        y ([float]):  Destanation Y.
        maxDist (int, optional): Distance to turn points to be considered a reached point. Defaults to 250.
        callback ([function], optional): Function callback called after reach destination. Defaults to None.
        mapName ([str], optional): The name of the map of the final destination, if is None it will use the current map. Defaults to None.
        mapLinks (list, optional): Reserved.

    Returns:
        [object]: Returns None on error.
    """
    return mapMovement.MoveToMapPosition((x,y),mapName,mapLinks,callback,maxDist)

    
def GoToPosition(x,y):
    """
    Move to (x,y) position without using pathfinding.

    Args:
        x ([float]): x
        y ([float]): y
    """
    Movement.GoStraightToPoint(x,y)

def StopMovement():
    """
    Stop Moving Action.
    """
    mapMovement.Stop()
    Movement.Stop()



def TeleportToPosition(dst_x,dst_y,max_packets=MAX_TELEPORT_PACKETS):
    import time
    """
    Teleport to a position by using pathfinding and telporting in multiple small steps.
    max_packets allows to avoid spamming the server and crash by putting a limit on maximum number of packets sent. 

    Args:
        dst_x ([float]): Destination X
        dst_y ([float]): Destination Y
        max_packets ([int], optional): Number maximum of positions packets to send. Defaults to MAX_TELEPORT_PACKETS.

    Returns:
        [int]: Returns the number of State packets sent.
    """
    if STATE_MOVING == Movement.state:
        StopMovement()
    x,y,z = player.GetMainCharacterPosition()
    points = eXLib.FindPath(x,y,dst_x,dst_y)
    if len(points) == 0:
        return None
    #chat.AppendChat(3,"Teleporting to X->" + str(dst_x) + "  Y->" + str(dst_y) + " Distance->" + str(OpenLib.dist(x,y,dst_x,dst_y)) + " Number of Points ->"+ str(len(points)))
    curr_x,curr_y = (x,y)
    dest_last_x, dest_last_y = points[0]
    counter = 0
    for point in points:
        dest1_x,dest1_y = point
        counter_,pos = TeleportStraightLine(curr_x,curr_y,dest_last_x, dest_last_y,max_packets-counter)
        counter += counter_
        if counter >= max_packets:
            chr.SelectInstance(net.GetMainActorVID())
            chr.SetPixelPosition(pos[0],pos[1])
            #chat.AppendChat(3,str(counter) + " packets sent.")
            time.sleep(TELEPORT_WAIT_TIME)
            return max_packets + TeleportToPosition(dst_x,dst_y,max_packets)
        curr_x,curr_y = (dest_last_x, dest_last_y)
        dest_last_x, dest_last_y = point

    counter_,pos = TeleportStraightLine(curr_x,curr_y,dest_last_x, dest_last_y,max_packets-counter)
    counter += counter_
    #chat.AppendChat(3,str(counter) + " packets sent.")
    
    chr.SelectInstance(net.GetMainActorVID())
    chr.SetPixelPosition(pos[0],pos[1])
    #Reload mobs
    eXLib.SendStatePacket(pos[0]-100,pos[1]-100,0.0,1,0)
    eXLib.SendStatePacket(pos[0]+100,pos[1]+100,0.0,1,0)
    return counter

Movement = MovementDialog()
mapMovement = MapMovementDialog()
    
          
        
            
        

        