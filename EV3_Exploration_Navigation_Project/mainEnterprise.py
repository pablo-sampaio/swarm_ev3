#!/usr/bin/env python3

# This programa is a tested implementation of ECEP (version 1) in a EV3, 
# assembled with the "Enterprise"shape (adapted), published in SBR/LARS 2019.

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
if len(sys.argv) > 1:
    NAVDATA_MAGIC_NUMBER_STR = ""
    for i in range(0,8):
        NAVDATA_MAGIC_NUMBER_STR += random.choice('0123456789ABCDEF')

robot = EnterpriseBot()
rfidReader = RfidSerialThread("COM5" if (platform.system() == "Windows") else "/dev/ttyUSB0")
brickButton = Button()

explorer = ExplorationManagerDfs3Simpl()
finishedExploration = False
lastTagTime = 0

RFID_TO_AXIS_DISTANCE = 4.0  #old: 5.7  # measure considering the axis as 0, and considering positive if should move forward to reach RFID reader

###################################
## FUNCTIONS

def dbgSleep(t=1.0):
    indebug = False
    if indebug:
        sleep(t)


def onNodeAction(nodeId):
    rfidReader.sendReadRequest(NAVDATA_RFID_ADDR, NAVDATA_MAGIC_NUMBER_STR)
    response = rfidReader.getReadResponse()
    while response is None:
        sleep(0.1)
        response = rfidReader.getReadResponse()

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
    if response[0] == True:
        nodeData.parseFrom(response[1])
        print(" - previous decdata:", nodeData)
    else:
        print(" - creating new decdata!")
        exits = detectAllLinesAround(robot)
        print(" - exits lines:", exits)
        nodeData.setup(len(exits))
        findLineNearby(robot)  # ensures that it returns to line

    nextRelativeExit = explorer.nextNode(nodeId, nodeData)

    if nodeData.changed:
        # volta para a posicao de leitura da tag
        robot.runMotorsDistance(RFID_TO_AXIS_DISTANCE, 150)
        dbgSleep()

        #  tentar escrever varias (3) vezes, tentar reposicionar o robo, etc
        print("Writting to RFID --", nodeData.toBytes())
        for i in range(1,5):
            print(" - trial", i)
            rfidReader.sendWriteRequest(NAVDATA_RFID_ADDR, NAVDATA_MAGIC_NUMBER_STR, nodeData.toBytes())
            resp = rfidReader.getWriteResponse()
            while (resp is None):
                resp = rfidReader.getWriteResponse()
                sleep(0.001)
            if resp[0]:
                break
            sleep(0.5)
        assert resp[0], "Could not write to RFID -- " + str(resp[1])  ## TODO: tive erros "error in hex string" -- pode ser timeout na leitura no Arduino
        print(" - ok")

        robot.runMotorsDistance(-RFID_TO_AXIS_DISTANCE, 150)
        dbgSleep()

    if nextRelativeExit != -1:
        global lastTagTime
        print("Going to line", nextRelativeExit)
        #input(" - press Enter to go...")
        goToNthLine(robot, nextRelativeExit)
        dbgSleep()
        print(" - ok")
        lastTagTime = time()
    else:
        global finishedExploration
        finishedExploration = True


def MAIN():
    global lastTagTime

    print("Starting RFID reader...")
    rfidReader.start()
    sleep(4)  # time for the RFID reader to start up

    findLineNearby(robot)

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

        if (time() - lastTagTime > 3) and rfidReader.getCurrentTagId() is not None:
            robot.stopMotors()
            Sound.beep()
            print("Tag detected - id", rfidReader.getCurrentTagId())
            dbgSleep()
            onNodeAction(rfidReader.getCurrentTagId())

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

