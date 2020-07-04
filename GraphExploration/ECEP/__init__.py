
from RfidReader import RfidSerialThread
from LinesNavigation import *
from time import sleep

##################################
# GLOBAL VARIABLES AND CONSTANTS #

NAVDATA_MAGIC_NUMBER_STR = "11a12a18"
NAVDATA_RFID_ADDR = 16

gLastNode = None
rfidReader = RfidSerialThread.getInstance()


##################################
# CLASSES                        #

class NodeMemory:
    """" Class that holds the navigation data in each node, as well as some (temporary) attributes used during exploration"""

    NOT_EXPLORED = b"00000000"   # mesmo tamanho da id da tag (8 digitos hexas)
    IN_EXPLORATION = b"00000001"
    
    def __init__(self, tagId):
        self.id = tagId
        self.nodes = None  # list of ids (from RFID tags) of the neighbors, ordered by clockwise exploration, each index is called a 'port'
        self.fmarked = False
        self.lastPort = -1
        self.changed = False

    def setup(self, n):
        self.nodes = n * [NodeMemory.NOT_EXPLORED]
        #self.fmarked = False
        #self.lastPort = -1
        self.changed = True

    # input example: b"[AABBCCDD,11223344,00000001]T,2"
    def parseFrom(self, dataBytes):
        assert dataBytes[0:1] == b'['
        i = 1
        self.nodes = []
        while True:
            self.nodes.append(dataBytes[i:i + 8])  # obs.: id tem 4 bytes == 8 digitos hexas
            i = i + 8
            if (dataBytes[i:(i + 1)] == b','):
                i = i + 1
                continue
            else:
                break
        assert dataBytes[i:(i + 1)] == b']'

        self.fmarked = (dataBytes[i+1:i+2] == b'T')
        assert dataBytes[i+2:i+3] == b','
        self.lastPort = int(dataBytes[i+3:])
        self.changed = False

    # atencao: nao estou usando a forma mais economica de representar os dados
    def toBytes(self):
        result = b'['
        for i in range(0, len(self.nodes)):
            result += self.nodes[i]
            result += b','
        if (len(self.nodes) > 0):
            result = result[0:-1]
        result += b']'
        result += b'T,' if self.fmarked else b'F,'
        result += str(self.lastPort).encode("ascii")
        return result

    def getId(self):
        return self.id

    def getNumNodes(self):  # number of neighbor nodes
        if self.nodes is None:
            return None
        return len(self.nodes)

    def getNode(self, port):
        return self.nodes[port]

    def setNode(self, port, neighborId):
        self.nodes[port] = neighborId
        self.changed = True

    def setInExploration(self, port):
        self.nodes[port] = NodeMemory.IN_EXPLORATION
        self.changed = True
  
    def getPortTo(self, neighborId):
        # could use nodes.index()
        for i in range(0, len(self.nodes)):
            if self.nodes[i] == neighborId:
                return i
        return -1

    def getUnexploredPort(self):
        for i in range(0, len(self.nodes)):
            if self.nodes[i] == NodeMemory.NOT_EXPLORED:
                return i
        return -1

    def isEmpty(self):
        for i in range(0, len(self.nodes)):
            if self.nodes[i] != NodeMemory.NOT_EXPLORED:  #or ==IN_EXPLORATION?
                return False
        return True

    def isComplete(self):
        for i in range(0, len(self.nodes)):
            if self.nodes[i] == NodeMemory.NOT_EXPLORED:  #or ==IN_EXPLORATION?
                return False
        return True

    def getLastPort(self):
        return self.lastPort

    def setLastPort(self, port):
        self.lastPort = port
        self.changed = True

    def isForwardMarked(self):
        return self.fmarked

    def setForwardMarked(self):
        self.fmarked = True
        self.changed = True

    def updateWith(self, port, targetNode):
        assert (self.nodes[port] == NodeMemory.IN_EXPLORATION), "Inconsistency updating data"
        self.nodes[port] = targetNode
        self.changed = True

    def __str__(self):
        res = str(self.nodes)
        res += str(self.fmarked) + ","
        res += str(self.lastPort)
        return res


class Move:
    FORWARD, BACKTRACK, FINISH = range(0, 3)


####################################
# EXPLORATION/NAVIGATION FUNCTIONS #

def _endForward(nodeData, lastNode, cost=None):
    firstVisit = not nodeData.fmarked and nodeData.isEmpty()

    # an undiscovered node
    if (firstVisit):
        print("- first time")
        print("- navData[node", nodeData.getId(), "] += (can-exit #0 -> node", lastNode, ")")
        nodeData.setForwardMarked()
        nodeData.setNode(0, lastNode)

    if (firstVisit and not nodeData.isComplete()):
        # a new (first-time) incomplete node
        port = nodeData.getUnexploredPort()
        nodeData.setInExploration(port)
        nodeData.setLastPort(port)
        return (Move.FORWARD, port)
    else:
        # complete node (may be a "new" node iff it has only 1 neighbor)
        # or a node already visited, incomplete, reached again
        print("- complete (in fwd move)")
        return (Move.BACKTRACK, 0)


def _endBacktrack(nodeData, lastNode, cost=None):
    nodeData.setNode(nodeData.getLastPort(), lastNode)
    delta = nodeData.getNumNodes()

    if not nodeData.isComplete():
        # an incomplete node
        canPort = nodeData.getUnexploredPort()
        nodeData.setInExploration(canPort)
        port = (canPort - nodeData.getLastPort()) % delta  # obs.: % never returns negative
        nodeData.setLastPort(canPort)
        print("- forward move (after bck), canon-port:", canPort, ", curr-port:", port)
        return (Move.FORWARD, port)

    elif nodeData.isForwardMarked():
        # backtracks
        port = (- nodeData.getLastPort()) % delta  # obs.: % never returns negative
        print("- backtrack (after bck), canon-port: 0 , curr-port:", port)
        return (Move.FORWARD, port)

    else:
        print("- finishing")
        return (Move.FINISH, -1)


def _dbgSleep(t=0.1):
    indebug = False
    if indebug:
        sleep(t)


def _readNodeMemory(robot):
    """
    Reads the navigation data from the current node.
    Robot start/end positions: from RFID to RFID.
    """

    global rfidReader
    tagId = rfidReader.getCurrentTagId()
    while tagId is None:
        print("Could not read RFID tag. Trying again...")
        sleep(1)
        tagId = rfidReader.getCurrentTagId()
    
    rfidReader.sendReadRequest(NAVDATA_RFID_ADDR, NAVDATA_MAGIC_NUMBER_STR)
    response = rfidReader.getReadResponse()
    while response is None:
        sleep(0.1)
        response = rfidReader.getReadResponse()

    print("Read answer:", response[1])
    nodeData = NodeMemory(tagId)
    if response[0] == True:
        nodeData.parseFrom(response[1])
        print(" - previous decdata:", nodeData)

    return nodeData


def _writeNodeMemory(robot, nodeData):
    """
    Writes the given navigation data to the current node.
    Robot start/end positions: from EDGE to EDGE.
    """

    global rfidReader

    robot.runMotorsDistance(robot.RFID_TO_AXIS_DISTANCE, 150) # volta para a posicao de leitura da tag
    _dbgSleep()

    # tentar escrever varias vezes, tentar reposicionar o robo, etc
    print("Writting to RFID --", nodeData.toBytes())
    response = None
    for i in range(1,7):
        print(" - trial", i)
        rfidReader.sendWriteRequest(NAVDATA_RFID_ADDR, NAVDATA_MAGIC_NUMBER_STR, nodeData.toBytes())
        response = rfidReader.getWriteResponse()
        while (response is None):
            response = rfidReader.getWriteResponse()
            sleep(0.001)
        if response[0]:
            break
        sleep(1)
    
    assert response[0], " - aborting, could not write to RFID -- " + str(response[1])
    print(" - ok")

    robot.runMotorsDistance(-robot.RFID_TO_AXIS_DISTANCE, 150) # posicao de arestas
    _dbgSleep()


def traverseAndRead(robot, port):
    """
    Finds the port-th edge in the clockwise direction, then traverses it,
    then reads the navigation data of the destination node.
    Robot start/end positions: from EDGE to EDGE.
    """

    goToNthLine(robot, port)

    #robot.resetDistance()
    
    # TODO: follow line... ate uma tag

    #cost = robot.getDistance()
    V = _readNodeMemory(robot)
    
    # goes back, to put the axis exactly over the tag, and its light sensors over the lines
    robot.runMotorsDistance(-robot.RFID_TO_AXIS_DISTANCE, 150)
    _dbgSleep()

    # turns back to properly count the lines starting from the line from where the robot
    # came used more than 180, in case something blocks it during the turn
    robot.turn(-180, 150)
    findLineNearby(robot)
    _dbgSleep()
    
    if (V.nodes is None):
        ports = detectAllLinesAround(robot)
        print(" - ports / lines:", len(ports))
        V.setup(len(ports))
        findLineNearby(robot)  # ensures that it returns to a line

    return V #,cost

# UNTESTED implementation of ECEP
def exploreGraph(robot):
    """
    Explore a graph with RFID tags in the nodes, using the ECEP algorithm.
    The robot should be started on a line, turned to the desired initial node.
    Returns the navigation data of the start node. After that, the robot should
    move from node to node using the navigateToNeighbor() function. The robot
    should not be manually moved to different nodes or edges.
    Robot start/end positions: from EDGE* (turned to the start node) to EDGE.
    """

    nodeData = traverseAndRead(robot, 0) # artifício para ler a memoria do 1o vertice, com esta funcao
    
    port = 0
    nodeData.setInExploration(0)
    nodeData.setLastPort(0)
    nextAction = Move.FORWARD
    lastNode = None

    while nextAction != Move.FINISH:
        lastNode = nodeData.getId()
        nodeData = traverseAndRead(robot, port) # entra na posicao edge, sai na posicao edge
        
        if nextAction == Move.FORWARD:
            (nextAction, port) = _endForward(nodeData, lastNode)
        elif nextAction == Move.BACKTRACK:
            (nextAction, port) = _endForward(nodeData, lastNode)

        if nodeData.changed:
            _writeNodeMemory(robot, nodeData) # entra na posicao edge, sai na posicao RFID

    global gLastNode
    gLastNode = lastNode  # used for navigation

    return nodeData


# UNTESTED implementation of initialization required by NCEP
def navigateInitialize(robot):
    """
    This function may be used to initialize the variables required by the other
    'navigate' functions.
    All the RFID tags must have been properly set up beforehand (e.g. by using the
    exploration procedure).
    The robot should be started on a line, turned to any initial node. The move will
    move to another node, than it returns the navigation data of the second node
    that can be used in the navigate functions.
    Robot start/end positions: from EDGE* (turned to the start node) to EDGE.
    """

    currNavData = traverseAndRead(robot, 0) # to read the 1st node's memory
    assert currNavData.isComplete()

    global gLastNode
    gLastNode = currNavData.getId()

    currNavData = traverseAndRead(robot, 0)
    assert currNavData.isComplete()

    return currNavData


# UNTESTED implementation of NCEP
def navigateToNeighbor(robot, currNavData, nextNode):
    """
    Goes to the given nextNode, which should be a neighbor of the current node
    (where the robot is placed when this function is called). The navigation data of
    the current node must be provided.
    Robot start/end positions: from EDGE to EDGE.
    """

    global gLastNode
    assert gLastNode is not None, "Variable gLastNode should be initialized -- use navigateInitialize()"

    p_last = currNavData.getPortTo(gLastNode)
    p_next = currNavData.getPortTo(nextNode)
    delta = currNavData.getNumNodes()
    p = (p_last - p_next + delta) % delta

    V = traverseAndRead(robot, p)
    assert V.getId() == nextNode
    assert V.isComplete()
    gLastNode = currNavData.getId()

    return V


def navigateFollowPath(robot, currNavData, path):
    """
    Controls the robot to follow a given path. Receives the navigation data of the
    current node of the robot.
    If you need to initialize, do it by placing the robot on another node turned
    to the first node of the path, then call the initialization, then this function.
    Robot start/end positions: from EDGE to EDGE.
    """

    global rfidReader
    assert gLastNode is not None
    rfidReader = RfidSerialThread.getInstance()

    robot.runMotorsDistance(-robot.RFID_TO_AXIS_DISTANCE, 150) # goes back, to read the tag

    print("Detecting initial node...")
    currNodeId = rfidReader.getCurrentTagId()
    while currNodeId is None:
        currNodeId = rfidReader.getCurrentTagId()
        sleep(0.1)

    robot.runMotorsDistance(+robot.RFID_TO_AXIS_DISTANCE, 150)
    assert currNodeId == path[0]

    index = 1
    while index < len(path):
        '''and not brickButton.any():'''
        currNavData = navigateToNeighbor(robot, currNavData, path[index])
        assert currNavData.getId() == path[index]
        index = index + 1

    robot.stopMotors()
    return currNavData

