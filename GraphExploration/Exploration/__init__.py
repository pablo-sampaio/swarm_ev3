##################################
## Class NODE MEMORY
## (Based on Java class NeighborListX)
class NavigationData:
    NOT_EXPLORED = b"00000000"   # mesmo tamanho da id da tag (8 digitos hexas)
    IN_EXPLORATION = b"00000001"

    def __init__(self):
        self.nodes = None  # list of ids (from RFID tags) of the neighbors, ordered by clockwise exploration
                           # each index is called a '(canonical) exit' of current node
        self.currExit = None
        self.ancestorPair = None
        self.new = None
        self.changed = False  # if it was changed since last time it was read
        # self.distances = None #+ number of updates to each distance

    def setup(self, n):
        self.nodes = n * [NavigationData.NOT_EXPLORED]
        self.currExit = 0
        self.ancestorPair = None
        self.new = True
        self.changed = True

    # input example: b"[AABBCCDD,11223344,33224455]45"
    # input example: b"[AABBCCDD,11223344,33224455]37(AABBCCDD,3)"
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
        j = dataBytes.find(b'(')
        if (j == -1):
            self.currExit = int(dataBytes[i+1:])
            self.ancestorPair = None
        else:
            self.currExit = int(dataBytes[i+1:j])
            k = dataBytes.rfind(b',') # finds the last comma
            fst = dataBytes[j+1:k]  # bytes object
            snd = int(dataBytes[k+1:-1])
            self.ancestorPair = (fst, snd)
            assert dataBytes[-1:] == b')'

        self.new = False
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
        result += str(self.currExit).encode("ascii")
        if (self.ancestorPair is not None):
            result += b'('
            result += self.ancestorPair[0]
            result += b','
            result += str(self.ancestorPair[1]).encode("ascii")
            result += b')'
        return result

    def getNumNodes(self):  # number of neighbor nodes
        if self.nodes is None:
            return None
        return len(self.nodes)

    def getNode(self, exit):
        return self.nodes[exit]

    def setNode(self, exit, neighborId):
        self.nodes[exit] = neighborId
        self.changed = True

    def setInExploration(self, exit):
        self.nodes[exit] = NavigationData.IN_EXPLORATION
        self.changed = True

    def getCurrentExit(self):
        return self.currExit

    def advanceToNextOpenExit(self):
        backupCurrExit = self.currExit
        if (self.currExit == len(self.nodes) - 1) or (self.currExit == -1):
            self.currExit = -1
        else:
            while (self.currExit < len(self.nodes)) and (self.nodes[self.currExit] != NavigationData.NOT_EXPLORED):
                self.currExit += 1
            if (self.currExit == len(self.nodes)):
                self.currExit = -1
        self.changed = (backupCurrExit != self.currExit)

    def getExitTo(self, neighborId):
        # could use nodes.index()
        for i in range(0, len(self.nodes)):
            if neighborId == self.nodes[i]:
                return i
        return -1

    def isComplete(self):
        return self.currExit == -1

    def getAncestorInfo(self):
        return self.ancestorPair

    def setAncestorInfo(self, info):
        self.ancestorPair = info

    def updateWith(self, exit, targetNode):
        assert (self.nodes[exit] == NavigationData.IN_EXPLORATION), "Inconsistency updating data"
        self.nodes[exit] = targetNode
        self.changed = True

    def __str__(self):
        res = str(self.nodes)
        res += str(self.currExit)
        if self.ancestorPair is not None:
            res += str(self.ancestorPair)
        return res


class Move:
    START, FORWARD, BACKTRACK, FINISH = range(0, 4)

##########################################
## Class EXPLORATION MANAGER DFS 3
## (Based on Java class DfsExplorer3MultiSimplified)
class ExplorationManagerDfs3Simpl:
    def __init__(self):
        self.nextAncestorInfo_fwd = None
        self.interruptedNode_bkt = -1
        self.backtrackedExit_bkt = -1
        self.destinyNodeDbg_bkt = -1
        self.currentMove = Move.START

    def nextNode(self, nodeId, nodeData):
        print("IN NODE", str(nodeId))
        assert (self.destinyNodeDbg_bkt == -1 or nodeId == self.destinyNodeDbg_bkt), "Unexpected neighbor - " + nodeId + " != " + self.destinyNodeDbg_bkt
        print("- nodedata:", str(nodeData))

        if self.currentMove == Move.START:
            print("- start node")
            return self._beginForwardMove(nodeId, nodeData, 0)
        elif self.currentMove == Move.FORWARD:
            return self._endForwardMove(nodeId, nodeData)
        elif self.currentMove == Move.BACKTRACK:
            return self._endBacktrack(nodeId, nodeData)
        elif self.currentMove == Move.FINISH:
            return -1
        else:
            raise Exception("Invalid move")

    def _endForwardMove(self, nodeId, nodeData):
        referenceExit = 0  # relative indexing == canonical indexing
        lastNode = self.nextAncestorInfo_fwd[0]
        print("- temp[node", lastNode, "] += (can-exit #", self.nextAncestorInfo_fwd[1], " -> node", nodeId, ")")

        # for an undiscovered node
        if (nodeData.new):
            print("- first time")
            print("- navData[node", nodeId, "] += (can-exit #0 -> node", lastNode, ")")
            nodeData.setNode(0, lastNode)
            nodeData.setAncestorInfo(self.nextAncestorInfo_fwd)  # ancestor data stored in the current node
            nodeData.advanceToNextOpenExit()

        if (nodeData.isComplete() or not nodeData.new):
            # complete node (may be a "new" node iff it has only 1 neighbor)
            # or a node already visited, incomplete, reached again
            print("- complete (in fwd move)")
            return self._beginBacktrack(True, nodeId, nodeData, self.nextAncestorInfo_fwd, 0)
        else:
            # a new (first-time) incomplete node
            return self._beginForwardMove(nodeId, nodeData, referenceExit)

    def _endBacktrack(self, nodeId, nodeData):
        referenceExit = self.backtrackedExit_bkt

        print("- synchronizing data for " + nodeId)
        nodeData.updateWith(self.backtrackedExit_bkt, self.interruptedNode_bkt)
        print("- nodedata updated:", nodeData)

        if nodeData.isComplete():
            ancestorInfo = nodeData.getAncestorInfo()
            if ancestorInfo == None:
                return self._finishMove()
            # backtracks
            print("- complete (bck move)")
            return self._beginBacktrack(False, nodeId, nodeData, ancestorInfo, referenceExit)
        else:
            # an incomplete node
            return self._beginForwardMove(nodeId, nodeData, referenceExit)

    def _beginForwardMove(self, nodeId, nodeData, referenceExit):
        nextCanonExit = nodeData.getCurrentExit()
        nextRelatExit = self._toRelativeExit(nextCanonExit, referenceExit, nodeData.getNumNodes())

        nodeData.setInExploration(nodeData.getCurrentExit())  # this exit/edge is being explored -- to be updated in the synchronization
        nodeData.advanceToNextOpenExit()
        print("- forward (can-exit #", nextCanonExit, ", rel-exit #", nextRelatExit, ")")

        self.nextAncestorInfo_fwd = (nodeId, nextCanonExit)
        self.currentMove = Move.FORWARD
        self.destinyNodeDbg_bkt = -1
        self.interruptedNode_bkt = -1
        self.backtrackedExit_bkt = -1
        return nextRelatExit

    def _beginBacktrack(self, afterForward, nodeId, nodeData, ancestorInfo, referenceExit):
        ancestorNode = ancestorInfo[0]

        if afterForward:
            nextRelatExit = 0  # return through the 'entrance' edge (for already-visited nodes reached in a forward move, because the reference is not properly set in this case)
            print("- backtrack to", ancestorNode, "(rel-exit #0)")
        else:
            nextCanonExit = nodeData.getExitTo(ancestorNode)
            nextRelatExit = self._toRelativeExit(nextCanonExit, referenceExit, nodeData.getNumNodes())
            assert (nextCanonExit != -1), "Error: map is not symetrical!"
            print("- backtrack to " + ancestorNode + " (can-exit #", nextCanonExit, ", rel-exit #", nextRelatExit, ")")

        self.destinyNodeDbg_bkt = ancestorNode  # for debugging only
        self.interruptedNode_bkt = nodeId
        self.backtrackedExit_bkt = ancestorInfo[1]
        self.currentMove = Move.BACKTRACK
        self.nextAncestorInfo_fwd = None
        return nextRelatExit

    def _finishMove(self):
        print("=> FINISHED ALL!")
        self.currentMove = Move.FINISH
        return -1  # stay in the same node

    def _toRelativeExit(self, canonicalExit, referenceExit, numEdges):
        return (canonicalExit - referenceExit + numEdges) % numEdges

    def _storeTempNavData(self, node, nodeExit, targetNode):
        self.tempNavData[node] = (nodeExit, targetNode)

    def _syncTempNavData(self, nodeData, node):
        if node in self.tempNavData.keys():
            pair = self.tempNavData.get(node)
            nodeData.updateWith(pair[0], pair[1])
            self.tempNavData.pop(node)
