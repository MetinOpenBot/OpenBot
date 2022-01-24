from OpenBot.Modules.NPCInteraction import NPCAction
import eXLib,OpenLib,os,net,FileManager,player,chat,background,NPCInteraction,OpenLog, Data



#list of MapLink found in module FileManager
map_links = list()

#list of maps
maps = dict()


#Use to give priority to own empire
CDD_1_KINDOMS = {
	"metin2_map_c1" : 3, #blues
	"metin2_map_b1" : 2, #reds?
	"metin2_map_a1" : 1, #yellow
}
CDD_2_KINDOMS = {
	"metin2_map_c3" : 3,
	"metin2_map_b3" : 2,
	"metin2_map_a3" : 1,
}



#Contains the links between maps
#map_origin and map_dest, are initialized as the maps names
#But are changed right after to reference the correct map
#And contains the action requires to got to the desired map
class MapLink():
	def __init__(self,x,y,map_origin,map_dest,race=0,event_answer = []):
		self.npc_action = NPCInteraction.NPCAction(race,(x,y),event_answer,map_origin)
		self.map_origin = map_origin
		self.map_dest = map_dest
		#chat.AppendChat(3,"Origin: " + str(map_origin) + " Dest: " + str(map_dest))

	def CrossMap(self):
		return self.npc_action.DoAction()

	def GetOriginMapName(self):
		return self.map_origin.map_name
		
	def GetDestMapName(self):
		return self.map_dest.map_name

	def GetOriginMap(self):
		return self.map_origin
	
	def GetDestMap(self):
		return self.map_dest

	def __str__(self):
		return str(self.map_origin) + " -> " + str(self.map_dest)

	def __repr__(self):
		return self.__str__()


#Helper Functions to evalute maps on search 
def EvaluateMapName(map,*args):
	return map.map_name == args[0]

def EvaluateMapNPC(map,*args):
	return map.HasNPC(args[0])

#MAIN MAP CLASS
#This class contains the npcs of each map and the links between maps
#Contain the npcs already parsed of each mas
class Map:
	def __init__(self,map_name):
		self.map_name = map_name
		self.npcs = FileManager.parseNpcList(map_name)
		OpenLog.DebugPrint("[Map-Manager] Map "+map_name + " has npcs="+str(self.npcs))
		self.links = dict()

	def SetMapLink(self,link):
		self.links[link.map_dest.map_name] = link


	def HasNPC(self,npc_race):
		if npc_race in self.npcs:
			return True
		return False

	#evaluateFunction represents should return true or false when a map is given
	def __GetClosestPath(self,level,path_buffer,evaluateFunction,*args):
		if level == 0:
			return False
		if evaluateFunction(self,*args):
			#chat.AppendChat(3,str(path_buffer)+"  "+str(level))
			return True

		for map_name,link in self.links.iteritems():
			#chat.AppendChat(3,"Push")
			path_buffer.append(link)
			presentInBuffer = False
			for link_visited in path_buffer:
				if link.GetDestMap() == link_visited.GetOriginMap():
					presentInBuffer = True
					break

			if not presentInBuffer and link.map_dest.__GetClosestPath(level-1,path_buffer,evaluateFunction,*args):
				return True
			else:
				path_buffer.pop()

		#chat.AppendChat(3,str(path_buffer))		
		return False

			
		

	#Get the closest path with the specified npc
	#Attention, this can be a very computational intensive task
	#If the own map has the npc, the map will be returned
	#If it is not found returns None and if it is found returns a list of links
	def GetClosestMapPathWithNPC(self,npc_race,max_depth = 7):
		buffer = list()
		if self.HasNPC(npc_race):
			return self
		for level in range(1,max_depth):
			buffer = list()
			val = self.__GetClosestPath(level,buffer,EvaluateMapNPC,npc_race)
			if val:
				break
		if len(buffer) == 0:
			return None
		
		#CHECK IF THERE ARE EQUIVLENT MAPS FROM OWN KINGDOM WITH THE SAME PATH

		#Check if city 1
		dest_map = buffer[-1].GetDestMapName()
		own_empire = Data.empireID
		if dest_map in CDD_1_KINDOMS and CDD_1_KINDOMS[dest_map] != own_empire:
			for mapName,kingId in CDD_1_KINDOMS.iteritems():
				if kingId == own_empire: 
					val = self.GetClosestMapPath(mapName)
					if len(val) != 0 and len(val) == len(buffer):
						return val
					else:
						return buffer 
		
		#Check if city 2
		if dest_map in CDD_2_KINDOMS and CDD_2_KINDOMS[dest_map] != own_empire:
			for mapName,kingId in CDD_2_KINDOMS.iteritems():
				if kingId == own_empire: 
					val = self.GetClosestMapPath(mapName)
					if len(val) != 0 and len(val) == len(buffer):
						return val
					else:
						return buffer 
		return buffer
		#Check if is city2

	
	
	#Get the closest path to the specified map
	#Attention, this can be a very computational intensive task
	#Check if the map first exist before calling this
	#Returns a list of links
	def GetClosestMapPath(self,dest_map_name,max_depth = 7):
		buffer = list()
		for level in range(0,max_depth):
			buffer = list()
			val = self.__GetClosestPath(level,buffer,EvaluateMapName,dest_map_name)
			if val:
				return buffer

		#chat.AppendChat(3,str(buffer))
		return buffer#.reverse()
	
	#Returns x,y position of closest npc or None if it is not available
	def GetNpcPositionClosest(self,npc_race,curr_x,curr_y):
		if npc_race not in self.npcs:
			return None

		min_dist = 1999999
		x_result = 0
		y_result = 0

		for x,y in self.npcs[npc_race]:
			dst = OpenLib.dist(curr_x,curr_y,x,y)
			if dst<min_dist:
				min_dist = dst
				x_result = x
				y_result = y
		
		return (x_result,y_result)

	def __str__(self):
		return self.map_name
	
	def __hash__(self):
		return self.map_name.__hash__()

	def __eq__(self, obj):
		return self.map_name.__eq__(obj)


def setLinks():
	lst = FileManager.parseMapLinks()
	for each in lst:
		#OpenLog.DebugPrint(each['race'])
		map_links.append(MapLink(each['x'],each['y'],each['orig'],each['dest'],each['race'],each['event_answer']))



def setMaps():
	setLinks()
	#Getting maps available
	map_names = set()
	for file in os.listdir(FileManager.CONFIG_MAP_NPCS):
		file_name = file.split(".")
		if len(file_name) == 2:
			if(file_name[1] == '.npcs'):
				map_names.add(file_name[0])

	for mapLink in map_links:
		map_names.add(mapLink.map_origin)
		map_names.add(mapLink.map_dest)

	#Create the Maps
	for map_name in map_names:
		maps[map_name] = Map(map_name)

	#Replace the map_names in links by the map object
	#And set map links in each map
	for link in map_links:
		link.map_origin = maps[link.map_origin]
		link.map_dest = maps[link.map_dest]
		maps[link.map_origin].SetMapLink(link)


#############################INTERFACE###################################

#Return a list of links
#Returns empty list if map is not configured or the starting map is the same as the end map
def GetMapPath(map_name_end,map_name_start=None):
	if map_name_start == None:
		map_name_start=background.GetCurrentMapName()
	if map_name_end == map_name_start:
		OpenLog.DebugPrint("[Map-Manager] start map and end map are the same.")
		return []
	if map_name_start in maps and map_name_end in maps:
		links = maps[map_name_start].GetClosestMapPath(map_name_end)
		OpenLog.DebugPrint(str(links))
		return links
	else:
		OpenLog.DebugPrint("[Map-Manager] Either " + map_name_start+" or "+ map_name_end + " are not configured.")
		return []

def GetMap(map_name=None):
	if map_name==None:
		map_name=background.GetCurrentMapName()
	if map_name in maps:
		return maps[map_name]
	else:
		OpenLog.DebugPrint("[Map-Manager] Map " + map_name+" doesn't exist.")
		return None

#Returns a tupple containing a list of links, and the map name
def GetClosestMapPathWithNPC(npc_race,map_name_start=None):
	if map_name_start == None:
		map_name_start=background.GetCurrentMapName()
	if map_name_start in maps:
		links = maps[map_name_start].GetClosestMapPathWithNPC(npc_race)
		if isinstance(links,Map):
			return [],links.map_name
		if type(links) == list:
			if len(links) == 0:
				return [],None
			return links,links[-1].GetDestMapName()

		return [],None
	else:
		OpenLog.DebugPrint(3,"[Map-Manager] Map " + map_name_start +" is not configured.")
		return [],None

#Return the closest position of the NPC in the specified map
def GetNpcFromMap(map_name,npc_race,position=None):
	if map_name== None:
		map_name=background.GetCurrentMapName()

	if position == None:
		position=player.GetMainCharacterPosition()
	#OpenLog.DebugPrint("Searching NPC race:"+str(npc_race) + " on map " + str(map_name))
	map = GetMap(map_name)
	if map != None and map.HasNPC(npc_race):
		return map.GetNpcPositionClosest(npc_race,position[0],position[1])
	
	OpenLog.DebugPrint("[Map-Manager] NPC not found! Race=" + str(npc_race) + " Map="+map_name)
	return None


setMaps()
	

