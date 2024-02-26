#!/usr/bin/env python3

# This program is a tested implementation of NCEP in a EV3, assembled 
# with the "Enterprise" shape (adapted), published in SBR/LARS 2019.

import platform
import sys
import random
from time import *
from ev3dev.ev3 import Button, Sound
from BotHardware import EnterpriseBot
from RfidReader import RfidSerialThread
from LinesNavigation import *
from Exploration import *


###################################
## CONSTANTS AND VARIABLES

NAVDATA_RFID_ADDR = 16

# this magic number must match with the one recorded in the tags to read their nav data (useful for a fully anotated graph)
# if a program input is given, a random magic number is generated, causing current navdata to be ignored and replaced
NAVDATA_MAGIC_NUMBER_STR = "11a12a18"

robot = EnterpriseBot()
rfidReader = RfidSerialThread("COM5" if (platform.system() == "Windows") else "/dev/ttyUSB0")
brickButton = Button()

lastTagTime = 0

RFID_TO_AXIS_DISTANCE = 4.0  #old: 5.7  # measure considering the axis as 0, and considering positive if should move forward to reach RFID reader

###################################
## FUNCTIONS

def dbgSleep(t=1.0):
    indebug = False
    if indebug:
        sleep(t)

def navigateNextPort(lastNode, nodeData, nextNode):
    p_last = nodeData.getExitTo(lastNode)
    p_next = nodeData.getExitTo(nextNode)
    delta = nodeData.getNumNodes()
    return (p_last - p_next + delta) % delta


def onNodeActionFollowPath(lastNodeId, nodeId, nextNodeId):
    rfidReader.sendReadRequest(NAVDATA_RFID_ADDR, NAVDATA_MAGIC_NUMBER_STR)
    response = rfidReader.getReadResponse()
    while response is None:
        sleep(0.1)
        response = rfidReader.getReadResponse()

    assert response[0] == True, "Could not parse data -- wrong magic number?"

    # goes back, to put the axis exactly over the tag
    robot.runMotorsDistance(-RFID_TO_AXIS_DISTANCE, 150)
    dbgSleep()

    # turns back to properly count the lines starting from the line from where the robot came
    # used more than 180, in case something blocks it during the turn
    robot.turn(-190, 150)
    findLineNearby(robot)
    dbgSleep()

    print("Read answer:", response[1])
    nodeData = NavigationData()
    nodeData.parseFrom(response[1])
    print(" - decdata:", nodeData)

    nextPort = navigateNextPort(lastNodeId, nodeData, nextNodeId)

    assert nextPort >= 0, "Invalid port!"
    global lastTagTime
    print("Going to line", nextPort)

    goToNthLine(robot, nextPort)
    dbgSleep()
    lastTagTime = time()


def FOLLOW_PATH(path):
    global lastTagTime

    print("Starting RFID reader...")
    rfidReader.start()
    sleep(4)  # time for the RFID reader to start up

    findLineNearby(robot)

    nd = 0
    lastNodeId = None # ATENCAO: precisa soltar do no anterior em direcao ao no que você deseja começar o caminho
    while not brickButton.any() and not finishedExploration:
        if (robot.getDistanceAhead() is None) or (robot.getDistanceAhead() >= 20):
            #go ahead
            robot.followLine(200)
        else:
            #shock prevention
            print("Obstacle at distance ", robot.getDistanceAhead(), "! Waiting...")  #IDEIA: este para, e o outro robo desvia
            robot.stopMotors()
            while robot.getDistanceAhead() < 20:
                sleep(0.1)
            print(" - clear to go...")
            robot.followLine(200)

        currentNodeId = rfidReader.getCurrentTagId()
        if (time() - lastTagTime > 3) and currentNodeId is not None:
            robot.stopMotors()
            Sound.beep()
            print("Tag detected - id", currentNodeId)
            dbgSleep()
            if lastNodeId is None:
                lastNodeId = currentNodeId
            else:
                assert currentNodeId == path[nd]
                nd = nd + 1
                onNodeActionFollowPath(lastNodeId, currentNodeId, path[nd])
                lastNodeId = currentNodeId

    robot.stopMotors()
    rfidReader.stop()
    return


#######################
### ENTRY POINT

try:
    MAIN()

except:
    print("Error. More info:")
    import traceback
    traceback.print_exc()
    robot.stopMotors("coast")
    rfidReader.stop()

